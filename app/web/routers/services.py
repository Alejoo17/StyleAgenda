from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.repositories.service_repository import ServiceRepository
from app.web.schemas.service import ServiceRead

router = APIRouter(prefix="/services", tags=["servicios"])


@router.get("", response_model=list[ServiceRead])
def list_services(session: Session = Depends(get_session)):
    return ServiceRepository(session).list_active()
