from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.domain.enums import AppointmentStatus


class AppointmentCreate(BaseModel):
    client_id: int
    barber_id: int
    service_id: int
    start_at: datetime


class RescheduleRequest(BaseModel):
    start_at: datetime


class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    client_id: int
    barber_id: int
    service_id: int
    start_at: datetime
    end_at: datetime
    price: Decimal
    status: AppointmentStatus
