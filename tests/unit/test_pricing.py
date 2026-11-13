from datetime import datetime
from decimal import Decimal
from app.services.pricing_service import PricingService


def test_regular_price_on_weekend():
    assert PricingService().calculate(Decimal("20000"), at=datetime(2026, 11, 15)) == Decimal("20000.00")


def test_frequent_discount_on_weekend():
    assert PricingService().calculate(Decimal("20000"), frequent=True,
                                      at=datetime(2026, 11, 15)) == Decimal("18000.00")


def test_weekday_promotion():
    assert PricingService().calculate(Decimal("20000"), frequent=True,
                                      at=datetime(2026, 11, 16)) == Decimal("17000.00")
