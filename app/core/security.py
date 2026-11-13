from passlib.context import CryptContext

_passwords = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    if len(password) < 8: raise ValueError("La contraseña debe tener al menos 8 caracteres")
    return _passwords.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _passwords.verify(password, password_hash)
