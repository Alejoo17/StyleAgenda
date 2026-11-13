from datetime import datetime
from decimal import Decimal
from app.domain.pricing.strategy import PricingStrategy


class RegularPricing(PricingStrategy):
    name = "Tarifa regular"
    def calculate(self, base_price: Decimal, *, frequent: bool = False,
                  at: datetime | None = None) -> Decimal:
        return Decimal(base_price).quantize(Decimal("0.01"))
