"""Pruebas de integración: autenticación multi-tenant y control de acceso por rol."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def _login(cliente: AsyncClient, **credenciales: str) -> str:
    respuesta = await cliente.post("/api/v1/auth/login", json=credenciales)
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()["access_token"]


async def test_login_con_credenciales_invalidas_es_rechazado(cliente: AsyncClient) -> None:
    respuesta = await cliente.post(
        "/api/v1/auth/login", json={"correo": "no-existe@conjunto.com", "password": "x"}
    )
    assert respuesta.status_code == 401
    assert respuesta.json()["codigo"] == "CREDENCIALES_INVALIDAS"


async def test_acceso_sin_token_es_rechazado(cliente: AsyncClient) -> None:
    respuesta = await cliente.get("/api/v1/residents")
    assert respuesta.status_code == 401


async def test_login_bloquea_tras_demasiados_intentos_fallidos(cliente: AsyncClient) -> None:
    credenciales = {"correo": "fuerza-bruta@conjunto.com", "password": "incorrecta"}
    for _ in range(5):
        respuesta = await cliente.post("/api/v1/auth/login", json=credenciales)
        assert respuesta.status_code == 401

    bloqueado = await cliente.post("/api/v1/auth/login", json=credenciales)
    assert bloqueado.status_code == 429
    assert bloqueado.json()["codigo"] == "DEMASIADOS_INTENTOS"


async def test_login_con_slug_de_otra_unidad_es_rechazado(
    cliente: AsyncClient, credenciales_super_admin: dict[str, str]
) -> None:
    respuesta = await cliente.post(
        "/api/v1/auth/login",
        json={
            "correo": credenciales_super_admin["correo"],
            "password": credenciales_super_admin["password"],
            "slug_unidad_negocio": "otra-unidad-que-no-es-la-suya",
        },
    )
    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "ACCESO_UNIDAD_NEGOCIO_INVALIDO"


async def test_vigilante_puede_ver_residentes_pero_no_crearlos(
    cliente: AsyncClient, credenciales_vigilante: dict[str, str]
) -> None:
    token = await _login(cliente, **credenciales_vigilante)
    headers = {"Authorization": f"Bearer {token}"}

    consulta = await cliente.get("/api/v1/residents", headers=headers)
    assert consulta.status_code == 200

    creacion = await cliente.post(
        "/api/v1/residents",
        headers=headers,
        json={
            "nombre": "Intento de vigilante",
            "documento": "999",
            "tipo_residente_id": 1,
            "apartamento_id": 1,
        },
    )
    assert creacion.status_code == 403
    assert creacion.json()["codigo"] == "PERMISO_DENEGADO"


async def test_vigilante_puede_consultar_placas(
    cliente: AsyncClient, credenciales_vigilante: dict[str, str]
) -> None:
    token = await _login(cliente, **credenciales_vigilante)
    respuesta = await cliente.get(
        "/api/v1/vehicles/plate/ABC123", headers={"Authorization": f"Bearer {token}"}
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["registrado"] is False


async def test_super_admin_puede_acceder_a_gestion_de_residentes(
    cliente: AsyncClient, credenciales_super_admin: dict[str, str]
) -> None:
    token = await _login(cliente, **credenciales_super_admin)
    respuesta = await cliente.get(
        "/api/v1/residents", headers={"Authorization": f"Bearer {token}"}
    )
    assert respuesta.status_code == 200


async def test_admin_plataforma_no_puede_gestionar_residentes(
    cliente: AsyncClient, credenciales_admin_plataforma: dict[str, str]
) -> None:
    token = await _login(cliente, **credenciales_admin_plataforma)
    respuesta = await cliente.get(
        "/api/v1/residents", headers={"Authorization": f"Bearer {token}"}
    )
    assert respuesta.status_code == 403


async def test_super_admin_no_puede_gestionar_unidades_de_negocio(
    cliente: AsyncClient, credenciales_super_admin: dict[str, str]
) -> None:
    token = await _login(cliente, **credenciales_super_admin)
    respuesta = await cliente.get(
        "/api/v1/business-units", headers={"Authorization": f"Bearer {token}"}
    )
    assert respuesta.status_code == 403
