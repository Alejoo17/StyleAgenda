from app.domain.enums import UserRole
from app.infrastructure.orm.user_model import UserModel
from app.repositories.user_repository import UserRepository


def test_user_repository_persists_and_reads(session):
    user = UserModel(name="Ada", email="ada@example.com", password_hash="hash", role=UserRole.BARBER)
    UserRepository(session).add(user)
    session.commit()
    found = UserRepository(session).by_email("ada@example.com")
    assert found is not None and found.id == user.id
    assert found.role == UserRole.BARBER
