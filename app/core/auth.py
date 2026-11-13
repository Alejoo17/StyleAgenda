from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.domain.enums import UserRole
from app.infrastructure.orm.user_model import UserModel


def current_user(request: Request, session: Session = Depends(get_session)) -> UserModel:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inicia sesión para continuar",
                            headers={"Location": "/auth/login"})
    user = session.get(UserModel, int(user_id))
    if user is None:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Sesión inválida")
    return user


def require_role(*roles: UserRole):
    def dependency(user: UserModel = Depends(current_user)) -> UserModel:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="No tienes permiso para acceder a esta sección")
        return user
    return dependency
