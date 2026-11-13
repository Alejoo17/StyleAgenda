from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.domain.enums import AppointmentEventType, AppointmentStatus, UserRole
from app.domain.exceptions import NotFoundError, ValidationError
from app.domain.notifications.appointment_subject import AppointmentSubject
from app.infrastructure.orm.appointment_model import AppointmentModel
from app.infrastructure.orm.service_model import ServiceModel
from app.infrastructure.orm.user_model import UserModel
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.user_repository import UserRepository
from app.services.availability_service import AvailabilityService
from app.services.pricing_service import PricingService


class AppointmentService:
    def __init__(self, session: Session, subject: AppointmentSubject | None = None,
                 pricing: PricingService | None = None):
        self.session = session
        self.appointments = AppointmentRepository(session)
        self.users = UserRepository(session)
        self.services = ServiceRepository(session)
        self.availability = AvailabilityService(self.appointments)
        self.subject = subject or AppointmentSubject()
        self.pricing = pricing or PricingService()

    def _calculate_end(self, service: ServiceModel, start: datetime) -> datetime:
        return start + timedelta(minutes=service.duration_minutes)

    def _validate_people(self, client_id: int, barber_id: int) -> tuple[UserModel, UserModel]:
        client, barber = self.users.get(client_id), self.users.get(barber_id)
        if client is None or client.role != UserRole.CLIENT: raise NotFoundError("Cliente no encontrado")
        if barber is None or barber.role != UserRole.BARBER: raise NotFoundError("Barbero no encontrado")
        return client, barber

    def _commit_and_notify(self, event: AppointmentEventType, appointment: AppointmentModel):
        self.session.commit()
        self.session.refresh(appointment)
        try: self.subject.notify(event.value, appointment)
        except Exception:  # no revertir una operación persistida por fallo de un listener
            import logging
            logging.getLogger(__name__).exception("Falló un listener de cita %s", appointment.id)
        return appointment

    def book(self, *, client_id: int, barber_id: int, service_id: int,
             start_at: datetime) -> AppointmentModel:
        client, _barber = self._validate_people(client_id, barber_id)
        service = self.services.get(service_id)
        if service is None or not service.active: raise NotFoundError("Servicio no encontrado o inactivo")
        start = start_at.replace(tzinfo=None) if start_at.tzinfo else start_at
        end = self._calculate_end(service, start)
        self.availability.assert_available(barber_id, start, end)
        frequent = len(self.appointments.list_for_client(client_id)) >= 5
        price = self.pricing.calculate(Decimal(service.base_price), frequent=frequent, at=start)
        appointment = AppointmentModel(client_id=client_id, barber_id=barber_id,
            service_id=service_id, start_at=start, end_at=end, price=price,
            status=AppointmentStatus.CONFIRMED)
        try:
            self.appointments.add(appointment)
            return self._commit_and_notify(AppointmentEventType.CONFIRMED, appointment)
        except Exception:
            self.session.rollback(); raise

    def cancel(self, appointment_id: int, *, client_id: int | None = None) -> AppointmentModel:
        appointment = self.appointments.get(appointment_id)
        if appointment is None: raise NotFoundError("Cita no encontrada")
        if client_id is not None and appointment.client_id != client_id: raise NotFoundError("Cita no encontrada")
        if appointment.status == AppointmentStatus.CANCELLED: raise ValidationError("La cita ya está cancelada")
        appointment.status = AppointmentStatus.CANCELLED
        return self._commit_and_notify(AppointmentEventType.CANCELLED, appointment)

    def reschedule(self, appointment_id: int, *, start_at: datetime,
                   client_id: int | None = None) -> AppointmentModel:
        appointment = self.appointments.get(appointment_id)
        if appointment is None: raise NotFoundError("Cita no encontrada")
        if client_id is not None and appointment.client_id != client_id: raise NotFoundError("Cita no encontrada")
        if appointment.status != AppointmentStatus.CONFIRMED: raise ValidationError("Solo se reprograman citas confirmadas")
        service = self.services.get(appointment.service_id)
        start = start_at.replace(tzinfo=None) if start_at.tzinfo else start_at
        end = self._calculate_end(service, start)
        self.availability.assert_available(appointment.barber_id, start, end, appointment.id)
        appointment.start_at, appointment.end_at = start, end
        return self._commit_and_notify(AppointmentEventType.RESCHEDULED, appointment)
