"""Listeners abstractos reutilizables; los adaptadores se definen en infraestructura."""
from app.domain.notifications.observer import AppointmentObserver


class AppointmentListener(AppointmentObserver):
    pass
