import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from app.infrastructure.orm import Base
from app.infrastructure import orm  # noqa: F401
from app.infrastructure.sqlite_database import SQLiteDatabase


@pytest.fixture
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as db:
        yield db
    engine.dispose()


@pytest.fixture(autouse=True)
def reset_singleton():
    SQLiteDatabase.reset_for_tests()
    yield
    SQLiteDatabase.reset_for_tests()
