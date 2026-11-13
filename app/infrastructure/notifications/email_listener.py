import logging
from app.domain.notifications.listeners import AppointmentListener

logger = logging.getLogger("styleagenda.events")


class EmailListener(AppointmentListener):
    """Adaptador demostrativo: registra el aviso; listo para sustituir por SMTP."""
    def update(self, event: str, appointment) -> None:
        logger.info("Observer EmailListener — aviso simulado (%s) para cliente_id=%s, cita_id=%s", event,
                    appointment.client_id, getattr(appointment, "id", None))
