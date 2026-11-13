from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.core.security import hash_password, verify_password
from app.domain.enums import UserRole
from app.domain.exceptions import ConflictError
from app.infrastructure.orm.user_model import UserModel
from app.repositories.user_repository import UserRepository
from app.services.user_factory import UserFactory
from app.web.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["autenticación y usuarios"])
pages_router = APIRouter(prefix="/auth", tags=["pantallas de acceso"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


@pages_router.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_page(request: Request, error: str | None = None):
    return templates.TemplateResponse(request, "auth/login.html", {"error": error})


@pages_router.post("/login", include_in_schema=False)
def login_form(request: Request, email: str = Form(...), password: str = Form(...),
               session: Session = Depends(get_session)):
    user = UserRepository(session).by_email(email)
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(request, "auth/login.html",
            {"error": "Correo o contraseña incorrectos"}, status_code=401)
    request.session.clear()
    request.session["user_id"] = user.id
    request.session["role"] = user.role.value
    if user.role == UserRole.ADMIN: target = "/admin/"
    elif user.role == UserRole.BARBER: target = "/barbers/"
    else: target = "/appointments/"
    return RedirectResponse(target, status_code=303)


@pages_router.post("/logout", include_in_schema=False)
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/auth/login", status_code=303)


@router.post("/users", response_model=UserRead, status_code=201)
def create_user(payload: UserCreate, session: Session = Depends(get_session)):
    if payload.role != UserRole.CLIENT:
        raise HTTPException(403, "El registro público solo permite crear clientes")
    repo = UserRepository(session)
    if repo.by_email(str(payload.email)): raise HTTPException(409, "El correo ya está registrado")
    try:
        entity = UserFactory.create(payload.role, name=payload.name, email=str(payload.email),
                                    password_hash=hash_password(payload.password))
        row = repo.add(UserModel(name=entity.name, email=entity.email,
                                 password_hash=entity.password_hash, role=entity.role))
        session.commit(); session.refresh(row); return row
    except Exception:
        session.rollback(); raise


@router.post("/login")
def login(request: Request, email: str, password: str, session: Session = Depends(get_session)):
    user = UserRepository(session).by_email(email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(401, "Credenciales inválidas")
    request.session.clear()
    request.session["user_id"] = user.id
    request.session["role"] = user.role.value
    return {"user_id": user.id, "name": user.name, "role": user.role.value}
