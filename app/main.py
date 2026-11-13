from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.core.database import database
from app.core.config import settings
from app.infrastructure.notifications.event_log import install_event_buffer
from app.web.routers import admin, appointments, auth, barbers, services
from app.web.routers import admin_portal, appointments_page, barber_portal


@asynccontextmanager
async def lifespan(_app: FastAPI):
    database.create_schema()
    install_event_buffer()
    yield


app = FastAPI(title="StyleAgenda API", version="0.1.0", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret,
    session_cookie="styleagenda_session", max_age=60 * 60 * 8,
    same_site="lax", https_only=settings.session_https_only)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
app.include_router(auth.pages_router)
app.include_router(appointments_page.router)
app.include_router(barber_portal.router)
app.include_router(admin_portal.router)
app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(services.router, prefix="/api")
app.include_router(barbers.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")


@app.get("/health", tags=["estado"])
def health(): return {"status": "ok"}


@app.get("/", include_in_schema=False)
def home(request: Request):
    if request.session.get("user_id"):
        role = request.session.get("role")
        if role == "CLIENT": return RedirectResponse("/appointments/", status_code=303)
        if role == "BARBER": return RedirectResponse("/barbers/", status_code=303)
        if role == "ADMIN": return RedirectResponse("/admin/", status_code=303)
    return RedirectResponse("/auth/login", status_code=303)
