from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.domain.enums import UserRole
from app.repositories.user_repository import UserRepository
from app.web.schemas.user import UserRead

router = APIRouter(prefix="/barbers", tags=["barberos"])


@router.get("", response_model=list[UserRead])
def list_barbers(session: Session = Depends(get_session)):
    return UserRepository(session).list_by_role(UserRole.BARBER)
