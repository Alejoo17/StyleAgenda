from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    BARBER = "BARBER"
    CLIENT = "CLIENT"


class AppointmentStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class AppointmentEventType(str, Enum):
    CONFIRMED = "confirmed"
    RESCHEDULED = "rescheduled"
    CANCELLED = "cancelled"
