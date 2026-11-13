import logging
from app.domain.notifications.listeners import AppointmentListener

logger = logging.getLogger("styleagenda.events")


class LogListener(AppointmentListener):
    def update(self, event: str, appointment) -> None:
        logger.info("Observer LogListener — cita %s: id=%s cliente=%s barbero=%s", event,
                    getattr(appointment, "id", None), appointment.client_id, appointment.barber_id)
