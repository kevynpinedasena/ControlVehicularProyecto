"""Pruebas de integración: gestión de usuarios por el Super Administrador de la unidad."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def _token(cliente: AsyncClient, **credenciales: str) -> str:
    respuesta = await cliente.post("/api/v1/auth/login", json=credenciales)
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()["access_token"]


async def test_usuario_creado_por_super_admin_puede_iniciar_sesion(
    cliente: AsyncClient, credenciales_super_admin: dict[str, str]
) -> None:
    """La contraseña debe quedar hasheada al crear el usuario, no almacenada en texto plano."""
    headers = {"Authorization": f"Bearer {await _token(cliente, **credenciales_super_admin)}"}

    creacion = await cliente.post(
        "/api/v1/users",
        headers=headers,
        json={
            "nombre": "Vigilante Nuevo",
            "correo": "vigilante-nuevo@conjunto.com",
            "password": "ClaveNueva123",
            "rol": "VIGILANTE",
        },
    )
    assert creacion.status_code == 201, creacion.text

    login = await cliente.post(
        "/api/v1/auth/login",
        json={
            "correo": "vigilante-nuevo@conjunto.com",
            "password": "ClaveNueva123",
            "slug_unidad_negocio": credenciales_super_admin["slug_unidad_negocio"],
        },
    )
    assert login.status_code == 200, login.text
