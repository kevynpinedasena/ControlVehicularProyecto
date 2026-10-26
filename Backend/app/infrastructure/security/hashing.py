"""Utilidades para el hashing seguro de contraseñas.

bcrypt es deliberadamente lento (~450ms por verificación) para resistir fuerza bruta. Llamarlo
de forma síncrona desde un endpoint async bloquea el único hilo del event loop de uvicorn: con
el servidor corriendo con un solo worker, un login congela la API para TODOS los tenants durante
esos ~450ms. Por eso `hashear_password_async`/`verificar_password_async` delegan a un hilo aparte
con `asyncio.to_thread`, y son las que se deben usar dentro de casos de uso (rutas HTTP). Las
versiones síncronas quedan para contextos fuera del event loop, como el script de siembra inicial.
"""
import asyncio

from passlib.context import CryptContext

_contexto_password = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashear_password(password: str) -> str:
    return _contexto_password.hash(password)


def verificar_password(password: str, password_hash: str) -> bool:
    return _contexto_password.verify(password, password_hash)


async def hashear_password_async(password: str) -> str:
    return await asyncio.to_thread(hashear_password, password)


async def verificar_password_async(password: str, password_hash: str) -> bool:
    return await asyncio.to_thread(verificar_password, password, password_hash)
