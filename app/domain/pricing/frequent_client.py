from datetime import datetime
from decimal import Decimal
from app.domain.pricing.strategy import PricingStrategy


class FrequentClientPricing(PricingStrategy):
    name = "Cliente frecuente (10% descuento)"
    def __init__(self, discount: Decimal = Decimal("0.10")):
        self.discount = discount

    def calculate(self, base_price: Decimal, *, frequent: bool = False,
                  at: datetime | None = None) -> Decimal:
        price = Decimal(base_price)
        return (price * (Decimal("1") - self.discount) if frequent else price).quantize(Decimal("0.01"))
