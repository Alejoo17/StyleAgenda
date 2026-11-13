from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal


class PricingStrategy(ABC):
    name = ""
    @abstractmethod
    def calculate(self, base_price: Decimal, *, frequent: bool = False,
                  at: datetime | None = None) -> Decimal: ...
