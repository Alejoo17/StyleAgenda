from fastapi import APIRouter, Depends, Request
from pathlib import Path
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.auth import require_role
from app.core.database import get_session
from app.domain.enums import UserRole
from app.infrastructure.orm.appointment_model import AppointmentModel
from app.infrastructure.orm.service_model import ServiceModel
from app.infrastructure.orm.user_model import UserModel

router = APIRouter(prefix="/barbers", tags=["portal del barbero"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def agenda(request: Request, session: Session = Depends(get_session),
           user: UserModel = Depends(require_role(UserRole.BARBER))):
    rows = session.execute(select(AppointmentModel, ServiceModel, UserModel).join(
        ServiceModel, AppointmentModel.service_id == ServiceModel.id).join(
        UserModel, AppointmentModel.client_id == UserModel.id).where(
        AppointmentModel.barber_id == user.id).order_by(AppointmentModel.start_at)).all()
    appointments = [{"appointment": a, "service": s, "client": c} for a, s, c in rows]
    return templates.TemplateResponse(request, "barbers/agenda.html",
        {"user": user, "appointments": appointments})
