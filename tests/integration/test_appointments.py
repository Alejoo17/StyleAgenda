from datetime import datetime
from decimal import Decimal
import pytest
from app.domain.enums import AppointmentStatus, UserRole
from app.domain.exceptions import ConflictError
from app.infrastructure.orm.appointment_model import AppointmentModel
from app.infrastructure.orm.service_model import ServiceModel
from app.infrastructure.orm.user_model import UserModel
from app.repositories.appointment_repository import AppointmentRepository
from app.services.appointment_service import AppointmentService


def setup_records(session):
    client = UserModel(name="Client", email="c@x.test", password_hash="hash", role=UserRole.CLIENT)
    barber = UserModel(name="Barber", email="b@x.test", password_hash="hash", role=UserRole.BARBER)
    service = ServiceModel(name="Corte", duration_minutes=30, base_price=Decimal("18000"), active=True)
    session.add_all([client, barber, service]); session.commit()
    return client, barber, service


def test_booking_persists_and_rejects_overlap(session):
    client, barber, service = setup_records(session)
    app_service = AppointmentService(session)
    appointment = app_service.book(client_id=client.id, barber_id=barber.id,
        service_id=service.id, start_at=datetime(2026, 11, 16, 9))
    assert session.get(AppointmentModel, appointment.id) is not None
    assert appointment.status == AppointmentStatus.CONFIRMED
    with pytest.raises(ConflictError):
        app_service.book(client_id=client.id, barber_id=barber.id,
            service_id=service.id, start_at=datetime(2026, 11, 16, 9, 15))


def test_adjacent_and_cancelled_slots_can_be_booked(session):
    client, barber, service = setup_records(session)
    service_api = AppointmentService(session)
    first = service_api.book(client_id=client.id, barber_id=barber.id,
        service_id=service.id, start_at=datetime(2026, 11, 16, 9))
    second = service_api.book(client_id=client.id, barber_id=barber.id,
        service_id=service.id, start_at=datetime(2026, 11, 16, 9, 30))
    service_api.cancel(first.id)
    third = service_api.book(client_id=client.id, barber_id=barber.id,
        service_id=service.id, start_at=datetime(2026, 11, 16, 9))
    assert third.id != second.id
    assert AppointmentRepository(session).get(first.id).status == AppointmentStatus.CANCELLED


def test_reschedule_notifies_observer(session):
    client, barber, service = setup_records(session)
    events = []
    class Listener:
        def update(self, event, appointment): events.append((event, appointment.id))
    from app.domain.notifications.appointment_subject import AppointmentSubject
    subject = AppointmentSubject(); subject.attach(Listener())
    service_api = AppointmentService(session, subject=subject)
    appointment = service_api.book(client_id=client.id, barber_id=barber.id,
        service_id=service.id, start_at=datetime(2026, 11, 16, 9))
    service_api.reschedule(appointment.id, start_at=datetime(2026, 11, 16, 11))
    assert ("confirmed", appointment.id) in events
    assert ("rescheduled", appointment.id) in events
