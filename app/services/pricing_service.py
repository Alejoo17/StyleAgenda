from datetime import datetime
from decimal import Decimal
from app.domain.pricing.frequent_client import FrequentClientPricing
from app.domain.pricing.regular import RegularPricing
from app.domain.pricing.weekday_promotion import WeekdayPromotionPricing
from app.domain.pricing.strategy import PricingStrategy


class PricingService:
    """Selecciona una estrategia; promo de día hábil prevalece sobre frecuencia."""
    def __init__(self, regular: PricingStrategy | None = None,
                 frequent: PricingStrategy | None = None,
                 weekday: PricingStrategy | None = None):
        self.regular = regular or RegularPricing()
        self.frequent = frequent or FrequentClientPricing()
        self.weekday = weekday or WeekdayPromotionPricing()

    def calculate(self, base_price: Decimal, *, frequent: bool = False,
                  at: datetime | None = None) -> Decimal:
        return self.quote(base_price, frequent=frequent, at=at)[0]

    def quote(self, base_price: Decimal, *, frequent: bool = False,
              at: datetime | None = None) -> tuple[Decimal, str]:
        if at is not None and at.weekday() < 5:
            strategy = self.weekday
        elif frequent:
            strategy = self.frequent
        else:
            strategy = self.regular
        return strategy.calculate(Decimal(base_price), frequent=frequent, at=at), strategy.name
