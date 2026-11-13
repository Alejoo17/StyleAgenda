from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class BarberService:
    name: str
    duration_minutes: int
    base_price: Decimal
    description: str = ""
    id: int | None = None


@dataclass(frozen=True)
class Corte(BarberService):
    name: str = "Corte"
    duration_minutes: int = 30
    base_price: Decimal = Decimal("18000")


@dataclass(frozen=True)
class Barba(BarberService):
    name: str = "Barba"
    duration_minutes: int = 25
    base_price: Decimal = Decimal("14000")


@dataclass(frozen=True)
class Combo(BarberService):
    name: str = "Combo"
    duration_minutes: int = 50
    base_price: Decimal = Decimal("28000")
