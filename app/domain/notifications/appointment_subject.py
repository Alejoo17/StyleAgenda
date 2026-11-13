from app.domain.notifications.observer import AppointmentObserver


class AppointmentSubject:
    def __init__(self):
        self._observers: list[AppointmentObserver] = []

    def attach(self, observer: AppointmentObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: AppointmentObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: str, appointment) -> None:
        for observer in tuple(self._observers):
            observer.update(event, appointment)
