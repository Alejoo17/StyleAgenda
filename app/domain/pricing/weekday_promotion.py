from datetime import datetime
from decimal import Decimal
from app.domain.pricing.strategy import PricingStrategy


class WeekdayPromotionPricing(PricingStrategy):
    name = "Promoción entre semana (15% descuento)"
    def __init__(self, discount: Decimal = Decimal("0.15")):
        self.discount = discount

    def calculate(self, base_price: Decimal, *, frequent: bool = False,
                  at: datetime | None = None) -> Decimal:
        price = Decimal(base_price)
        # Lunes-viernes. La promoción prevalece sobre el descuento frecuente.
        return (price * (Decimal("1") - self.discount)
                if at is not None and at.weekday() < 5 else price).quantize(Decimal("0.01"))
