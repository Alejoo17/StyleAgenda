from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import require_role
from app.core.database import get_session
from app.core.dependencies import appointment_subject
from app.domain.enums import UserRole
from app.domain.exceptions import ConflictError, NotFoundError, ValidationError
from app.infrastructure.orm.user_model import UserModel
from app.domain.notifications.appointment_subject import AppointmentSubject
from app.services.appointment_service import AppointmentService
from app.web.schemas.appointment import AppointmentCreate, AppointmentRead, RescheduleRequest

router = APIRouter(prefix="/appointments", tags=["citas"])


def _service(session: Session, subject: AppointmentSubject):
    return AppointmentService(session, subject=subject)


def _translate(exc: Exception):
    if isinstance(exc, ConflictError): raise HTTPException(409, str(exc)) from exc
    if isinstance(exc, NotFoundError): raise HTTPException(404, str(exc)) from exc
    if isinstance(exc, ValidationError): raise HTTPException(422, str(exc)) from exc
    raise exc


@router.post("", response_model=AppointmentRead, status_code=201)
def book(payload: AppointmentCreate, session: Session = Depends(get_session),
         subject: AppointmentSubject = Depends(appointment_subject),
         user: UserModel = Depends(require_role(UserRole.CLIENT))):
    try: return _service(session, subject).book(client_id=user.id, barber_id=payload.barber_id,
        service_id=payload.service_id, start_at=payload.start_at)
    except (ConflictError, NotFoundError, ValidationError) as exc: _translate(exc)


@router.patch("/{appointment_id}/reschedule", response_model=AppointmentRead)
def reschedule(appointment_id: int, payload: RescheduleRequest,
               session: Session = Depends(get_session),
               subject: AppointmentSubject = Depends(appointment_subject),
               user: UserModel = Depends(require_role(UserRole.CLIENT))):
    try: return _service(session, subject).reschedule(appointment_id,
        start_at=payload.start_at, client_id=user.id)
    except (ConflictError, NotFoundError, ValidationError) as exc: _translate(exc)


@router.post("/{appointment_id}/cancel", response_model=AppointmentRead)
def cancel(appointment_id: int, session: Session = Depends(get_session),
           subject: AppointmentSubject = Depends(appointment_subject),
           user: UserModel = Depends(require_role(UserRole.CLIENT))):
    try: return _service(session, subject).cancel(appointment_id, client_id=user.id)
    except (ConflictError, NotFoundError, ValidationError) as exc: _translate(exc)
