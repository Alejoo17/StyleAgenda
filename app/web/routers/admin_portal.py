import asyncio
import json
from pathlib import Path
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.core.auth import require_role
from app.core.database import get_session
from app.domain.enums import AppointmentStatus, UserRole
from app.infrastructure.notifications.event_log import event_buffer
from app.infrastructure.orm.appointment_model import AppointmentModel
from app.infrastructure.orm.service_model import ServiceModel
from app.infrastructure.orm.user_model import UserModel

router = APIRouter(prefix="/admin", tags=["portal administrador"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))
admin_only = require_role(UserRole.ADMIN)


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard(request: Request, session: Session = Depends(get_session),
              user: UserModel = Depends(admin_only), message: str | None = None):
    # Alias para distinguir el registro del cliente y el del barbero.
    from sqlalchemy.orm import aliased
    Barber = aliased(UserModel)
    rows = session.execute(select(AppointmentModel, ServiceModel, UserModel, Barber).join(
        ServiceModel, AppointmentModel.service_id == ServiceModel.id).join(
        UserModel, AppointmentModel.client_id == UserModel.id).join(
        Barber, AppointmentModel.barber_id == Barber.id).order_by(
        AppointmentModel.start_at.desc()).limit(100)).all()
    appointments = [{"appointment": a, "service": s, "client": c, "barber": b}
                    for a, s, c, b in rows]
    metrics = {"appointments": session.scalar(select(func.count()).select_from(AppointmentModel)) or 0,
        "confirmed": session.scalar(select(func.count()).select_from(AppointmentModel).where(
            AppointmentModel.status == AppointmentStatus.CONFIRMED)) or 0,
        "clients": session.scalar(select(func.count()).select_from(UserModel).where(
            UserModel.role == UserRole.CLIENT)) or 0,
        "services": session.scalar(select(func.count()).select_from(ServiceModel).where(
            ServiceModel.active.is_(True))) or 0}
    services = list(session.scalars(select(ServiceModel).order_by(ServiceModel.name)))
    return templates.TemplateResponse(request, "admin/dashboard.html", {
        "user": user, "appointments": appointments, "metrics": metrics,
        "services": services, "message": message, "events": event_buffer.latest(30)})


@router.post("/services", include_in_schema=False)
def create_service(name: str = Form(...), duration_minutes: int = Form(...),
                   base_price: float = Form(...), description: str = Form(""),
                   session: Session = Depends(get_session), user: UserModel = Depends(admin_only)):
    if duration_minutes <= 0 or base_price <= 0:
        return RedirectResponse("/admin/?message=Duración+y+precio+deben+ser+positivos", status_code=303)
    session.add(ServiceModel(name=name, duration_minutes=duration_minutes,
                             base_price=base_price, description=description, active=True))
    try: session.commit()
    except Exception:
        session.rollback()
        return RedirectResponse("/admin/?message=No+se+pudo+crear+el+servicio+(nombre+duplicado)", status_code=303)
    return RedirectResponse("/admin/?message=Servicio+creado", status_code=303)


@router.get("/events/recent", include_in_schema=False)
def recent_events(_user: UserModel = Depends(admin_only)):
    return event_buffer.latest()


@router.get("/events/stream", include_in_schema=False)
async def events_stream(request: Request, _user: UserModel = Depends(admin_only)):
    async def stream():
        cursor = 0
        for event in event_buffer.latest(): cursor = max(cursor, event["id"])
        while not await request.is_disconnected():
            events = event_buffer.after(cursor)
            for event in events:
                cursor = event["id"]
                yield f"id: {cursor}\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"
            if not events: yield ": keep-alive\n\n"
            await asyncio.sleep(1)
    return StreamingResponse(stream(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
