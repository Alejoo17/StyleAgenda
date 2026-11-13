from decimal import Decimal
from app.domain.entities.service import BarberService, Barba, Combo, Corte


class ServiceFactory:
    """Factory Method para los servicios conocidos de la barbería."""
    _types = {"corte": Corte, "barba": Barba, "combo": Combo}

    @classmethod
    def create(cls, kind: str, *, duration_minutes: int | None = None,
               base_price: Decimal | None = None, description: str = "") -> BarberService:
        key = kind.strip().casefold()
        if key not in cls._types: raise ValueError(f"Servicio no soportado: {kind}")
        defaults = cls._types[key]()
        return cls._types[key](
            name=defaults.name, duration_minutes=duration_minutes or defaults.duration_minutes,
            base_price=Decimal(base_price) if base_price is not None else defaults.base_price,
            description=description,
        )
