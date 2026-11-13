from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.domain.enums import AppointmentStatus


@dataclass(frozen=True)
class Appointment:
    client_id: int
    barber_id: int
    service_id: int
    start_at: datetime
    end_at: datetime
    price: Decimal
    status: AppointmentStatus = AppointmentStatus.CONFIRMED
    id: int | None = None
