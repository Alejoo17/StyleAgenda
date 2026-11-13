import pytest
from app.domain.enums import UserRole
from app.domain.entities.user import Admin, Barber, Client
from app.domain.entities.service import Corte, Barba, Combo
from app.services.user_factory import UserFactory
from app.services.service_factory import ServiceFactory
from app.infrastructure.sqlite_database import SQLiteDatabase


def test_sqlite_database_is_singleton():
    first = SQLiteDatabase("sqlite://")
    second = SQLiteDatabase("sqlite://")
    assert first is second
    assert first.engine is second.engine
    assert first.session_factory is second.session_factory


@pytest.mark.parametrize(("role", "expected"), [
    (UserRole.ADMIN, Admin), (UserRole.BARBER, Barber), (UserRole.CLIENT, Client),
])
def test_user_factory(role, expected):
    user = UserFactory.create(role, name="Test", email="test@example.com", password_hash="hash")
    assert isinstance(user, expected)
    assert user.role is role


@pytest.mark.parametrize(("kind", "expected"), [
    ("corte", Corte), ("barba", Barba), ("combo", Combo),
])
def test_service_factory(kind, expected):
    assert isinstance(ServiceFactory.create(kind), expected)


def test_factories_reject_unknown_type():
    with pytest.raises(ValueError): UserFactory.create("UNKNOWN", name="n", email="e", password_hash="h")
    with pytest.raises(ValueError): ServiceFactory.create("tinte")
