from datetime import datetime
from app.domain.exceptions import ConflictError, ValidationError
from app.repositories.appointment_repository import AppointmentRepository


class AvailabilityService:
    def __init__(self, appointments: AppointmentRepository): self.appointments = appointments

    def assert_available(self, barber_id: int, new_start: datetime, new_end: datetime,
                         exclude_appointment_id: int | None = None) -> None:
        if new_start >= new_end: raise ValidationError("La hora de inicio debe ser anterior al fin")
        if new_start.tzinfo is not None and new_start.utcoffset() is not None:
            new_start, new_end = new_start.replace(tzinfo=None), new_end.replace(tzinfo=None)
        conflicts = self.appointments.overlapping(barber_id, new_start, new_end, exclude_appointment_id)
        if conflicts:
            raise ConflictError("El barbero ya tiene una cita que se cruza con ese horario")
