from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.core.auth import require_role
from app.domain.enums import UserRole
from app.infrastructure.orm.service_model import ServiceModel
from app.repositories.service_repository import ServiceRepository
from app.web.schemas.service import ServiceCreate, ServiceRead

router = APIRouter(prefix="/admin/services", tags=["administración"])


@router.post("", response_model=ServiceRead, status_code=201)
def create_service(payload: ServiceCreate, session: Session = Depends(get_session),
                   _user=Depends(require_role(UserRole.ADMIN))):
    repo = ServiceRepository(session)
    if repo.by_name(payload.name): raise HTTPException(409, "El servicio ya existe")
    row = ServiceModel(**payload.model_dump())
    repo.add(row); session.commit(); session.refresh(row); return row
