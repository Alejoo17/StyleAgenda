from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.domain.enums import AppointmentStatus
from app.infrastructure.orm.appointment_model import AppointmentModel


class AppointmentRepository:
    def __init__(self, session: Session): self.session = session
    def get(self, appointment_id: int): return self.session.get(AppointmentModel, appointment_id)
    def add(self, appointment: AppointmentModel): self.session.add(appointment); self.session.flush(); return appointment
    def overlapping(self, barber_id: int, new_start: datetime, new_end: datetime,
                    exclude_id: int | None = None):
        stmt = select(AppointmentModel).where(
            AppointmentModel.barber_id == barber_id,
            AppointmentModel.status != AppointmentStatus.CANCELLED,
            AppointmentModel.start_at < new_end,
            AppointmentModel.end_at > new_start,
        )
        if exclude_id is not None: stmt = stmt.where(AppointmentModel.id != exclude_id)
        return list(self.session.scalars(stmt))
    def list_for_client(self, client_id: int):
        return list(self.session.scalars(select(AppointmentModel).where(AppointmentModel.client_id == client_id)))
