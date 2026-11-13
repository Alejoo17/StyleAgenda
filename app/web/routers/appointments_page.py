from datetime import datetime
from decimal import Decimal
from pathlib import Path
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.auth import require_role
from app.core.database import get_session
from app.core.dependencies import appointment_subject
from app.domain.enums import AppointmentStatus, UserRole
from app.domain.exceptions import ConflictError, NotFoundError, ValidationError
from app.domain.notifications.appointment_subject import AppointmentSubject
from app.infrastructure.orm.appointment_model import AppointmentModel
from app.infrastructure.orm.service_model import ServiceModel
from app.infrastructure.orm.user_model import UserModel
from app.services.appointment_service import AppointmentService
from app.services.pricing_service import PricingService

router = APIRouter(prefix="/appointments", tags=["portal del cliente"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))
client_only = require_role(UserRole.CLIENT)


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def portal(request: Request, session: Session = Depends(get_session), user: UserModel = Depends(client_only),
           message: str | None = None, error: str | None = None):
    services = list(session.scalars(select(ServiceModel).where(ServiceModel.active.is_(True))))
    barbers = list(session.scalars(select(UserModel).where(UserModel.role == UserRole.BARBER)))
    appointments = list(session.scalars(select(AppointmentModel).where(
        AppointmentModel.client_id == user.id).order_by(AppointmentModel.start_at.desc())))
    service_names = {s.id: s.name for s in services}
    barber_names = {b.id: b.name for b in barbers}
    return templates.TemplateResponse(request, "appointments/client.html", {
        "user": user, "services": services, "barbers": barbers, "appointments": appointments,
        "service_names": service_names, "barber_names": barber_names,
        "message": message, "error": error,
    })


@router.get("/quote", include_in_schema=False)
def quote(service_id: int, start_at: datetime, session: Session = Depends(get_session),
          user: UserModel = Depends(client_only)):
    service = session.get(ServiceModel, service_id)
    if service is None or not service.active:
        from fastapi import HTTPException
        raise HTTPException(404, "Servicio no encontrado")
    frequent_count = len(session.scalars(select(AppointmentModel.id).where(
        AppointmentModel.client_id == user.id).limit(5)).all())
    amount, strategy_name = PricingService().quote(Decimal(service.base_price),
        frequent=frequent_count >= 5, at=start_at)
    return {"price": str(amount), "strategy": strategy_name,
            "duration_minutes": service.duration_minutes}


@router.post("/book", include_in_schema=False)
def book(request: Request, service_id: int = Form(...), barber_id: int = Form(...),
         start_at: datetime = Form(...), session: Session = Depends(get_session),
         user: UserModel = Depends(client_only), subject: AppointmentSubject = Depends(appointment_subject)):
    try:
        AppointmentService(session, subject=subject).book(client_id=user.id, barber_id=barber_id,
            service_id=service_id, start_at=start_at)
        return RedirectResponse("/appointments/?message=Cita+confirmada+correctamente", status_code=303)
    except ConflictError as exc:
        return RedirectResponse(f"/appointments/?error={str(exc)}", status_code=303)
    except (NotFoundError, ValidationError) as exc:
        return RedirectResponse(f"/appointments/?error={str(exc)}", status_code=303)


@router.post("/{appointment_id}/reschedule", include_in_schema=False)
def reschedule(appointment_id: int, start_at: datetime = Form(...),
               user: UserModel = Depends(client_only), session: Session = Depends(get_session),
               subject: AppointmentSubject = Depends(appointment_subject)):
    try:
        AppointmentService(session, subject=subject).reschedule(appointment_id,
            start_at=start_at, client_id=user.id)
        return RedirectResponse("/appointments/?message=Cita+reprogramada+correctamente", status_code=303)
    except (ConflictError, NotFoundError, ValidationError) as exc:
        return RedirectResponse(f"/appointments/?error={str(exc)}", status_code=303)


@router.post("/{appointment_id}/cancel", include_in_schema=False)
def cancel(appointment_id: int, user: UserModel = Depends(client_only),
           session: Session = Depends(get_session),
           subject: AppointmentSubject = Depends(appointment_subject)):
    try:
        AppointmentService(session, subject=subject).cancel(appointment_id, client_id=user.id)
        return RedirectResponse("/appointments/?message=Cita+cancelada", status_code=303)
    except (NotFoundError, ValidationError) as exc:
        return RedirectResponse(f"/appointments/?error={str(exc)}", status_code=303)
