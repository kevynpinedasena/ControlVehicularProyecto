"""Utilidades para el hashing seguro de contraseñas."""
from passlib.context import CryptContext

_contexto_password = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashear_password(password: str) -> str:
    return _contexto_password.hash(password)


def verificar_password(password: str, password_hash: str) -> bool:
    return _contexto_password.verify(password, password_hash)
