from dataclasses import dataclass

from app.domain.enums import UserRole


@dataclass(frozen=True)
class User:
    name: str
    email: str
    password_hash: str
    role: UserRole
    id: int | None = None


@dataclass(frozen=True)
class Admin(User):
    role: UserRole = UserRole.ADMIN


@dataclass(frozen=True)
class Barber(User):
    role: UserRole = UserRole.BARBER


@dataclass(frozen=True)
class Client(User):
    role: UserRole = UserRole.CLIENT
