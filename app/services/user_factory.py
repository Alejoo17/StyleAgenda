from app.domain.entities.user import Admin, Barber, Client, User
from app.domain.enums import UserRole


class UserFactory:
    """Factory Method: selecciona el producto concreto según el rol."""
    _types = {UserRole.ADMIN: Admin, UserRole.BARBER: Barber, UserRole.CLIENT: Client}

    @classmethod
    def create(cls, role: UserRole | str, *, name: str, email: str,
               password_hash: str) -> User:
        try: user_type = cls._types[UserRole(role)]
        except (ValueError, KeyError) as exc: raise ValueError(f"Rol no soportado: {role}") from exc
        return user_type(name=name, email=email, password_hash=password_hash)
