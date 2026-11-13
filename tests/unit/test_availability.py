from datetime import datetime
from types import SimpleNamespace
import pytest
from app.domain.exceptions import ConflictError
from app.services.availability_service import AvailabilityService


class FakeAppointmentRepository:
    def __init__(self, rows): self.rows = rows
    def overlapping(self, barber_id, start, end, exclude_id=None):
        return [row for row in self.rows if row.barber_id == barber_id
                and row.id != exclude_id and row.status != "CANCELLED"
                and start < row.end_at and end > row.start_at]


def dt(hour, minute=0): return datetime(2026, 11, 16, hour, minute)


def test_adjacent_half_open_appointments_are_available():
    repo = FakeAppointmentRepository([SimpleNamespace(id=1, barber_id=4, start_at=dt(9), end_at=dt(10), status="CONFIRMED")])
    AvailabilityService(repo).assert_available(4, dt(10), dt(11))


@pytest.mark.parametrize(("start", "end"), [(dt(9, 30), dt(10, 30)), (dt(8), dt(11)), (dt(9), dt(10))])
def test_overlapping_appointments_conflict(start, end):
    repo = FakeAppointmentRepository([SimpleNamespace(id=1, barber_id=4, start_at=dt(9), end_at=dt(10), status="CONFIRMED")])
    with pytest.raises(ConflictError): AvailabilityService(repo).assert_available(4, start, end)


def test_cancelled_appointment_is_excluded():
    repo = FakeAppointmentRepository([SimpleNamespace(id=1, barber_id=4, start_at=dt(9), end_at=dt(10), status="CANCELLED")])
    AvailabilityService(repo).assert_available(4, dt(9, 15), dt(9, 45))
