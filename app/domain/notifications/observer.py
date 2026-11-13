from abc import ABC, abstractmethod
from typing import Any


class AppointmentObserver(ABC):
    @abstractmethod
    def update(self, event: str, appointment: Any) -> None: ...
