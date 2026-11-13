"""Buffer en memoria para que la sustentación muestre los logs del Observer en vivo."""
import logging
from collections import deque
from datetime import datetime, timezone
from threading import Lock


class EventBufferHandler(logging.Handler):
    def __init__(self, capacity: int = 250):
        super().__init__(logging.INFO)
        self.events = deque(maxlen=capacity)
        self._lock = Lock()
        self._next_id = 1

    def emit(self, record: logging.LogRecord) -> None:
        with self._lock:
            self.events.append({"id": self._next_id,
                "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
                "message": self.format(record)})
            self._next_id += 1

    def latest(self, limit: int = 50) -> list[dict]:
        with self._lock: return list(self.events)[-limit:]

    def after(self, event_id: int) -> list[dict]:
        with self._lock: return [event for event in self.events if event["id"] > event_id]


event_buffer = EventBufferHandler()


def install_event_buffer() -> None:
    logger = logging.getLogger("styleagenda.events")
    if event_buffer not in logger.handlers:
        logger.addHandler(event_buffer)
    logger.setLevel(logging.INFO)
