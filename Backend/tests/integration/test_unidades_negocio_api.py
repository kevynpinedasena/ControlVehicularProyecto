"""Pruebas de integración: administración de unidades de negocio (plataforma)."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def _token_plataforma(cliente: AsyncClient, credenciales_admin_plataforma: dict[str, str]) -> str:
    respuesta = await cliente.post("/api/v1/auth/login", json=credenciales_admin_plataforma)
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()["access_token"]


async def test_crear_unidad_negocio_y_su_super_admin(
    cliente: AsyncClient, credenciales_admin_plataforma: dict[str, str]
) -> None:
    headers = {"Authorization": f"Bearer {await _token_plataforma(cliente, credenciales_admin_plataforma)}"}

    respuesta = await cliente.post(
        "/api/v1/business-units",
        headers=headers,
        data={
            "nombre": "Conjunto Los Pinos",
            "slug": "Los Pinos!",
            "admin_nombre": "Ana Gómez",
            "admin_correo": "ana@lospinos.com",
            "admin_password": "ClaveSegura123",
            "color_primario": "#123456",
            "color_secundario": "#654321",
        },
    )
    assert respuesta.status_code == 201, respuesta.text
    unidad = respuesta.json()
    assert unidad["slug"] == "los-pinos"  # normalizado

    publica = await cliente.get(f"/api/v1/business-units/public/{unidad['slug']}")
    assert publica.status_code == 200
    assert publica.json()["nombre"] == "Conjunto Los Pinos"
    assert publica.json()["activo"] is True

    login_super_admin = await cliente.post(
        "/api/v1/auth/login",
        json={
            "correo": "ana@lospinos.com",
            "password": "ClaveSegura123",
            "slug_unidad_negocio": "los-pinos",
        },
    )
    assert login_super_admin.status_code == 200, login_super_admin.text


async def test_slug_duplicado_es_rechazado(
    cliente: AsyncClient, credenciales_admin_plataforma: dict[str, str]
) -> None:
    headers = {"Authorization": f"Bearer {await _token_plataforma(cliente, credenciales_admin_plataforma)}"}
    payload = {
        "nombre": "Conjunto A",
        "slug": "duplicado",
        "admin_nombre": "Admin A",
        "admin_correo": "adminA@conjunto.com",
        "admin_password": "ClaveSegura123",
    }
    primera = await cliente.post("/api/v1/business-units", headers=headers, data=payload)
    assert primera.status_code == 201

    payload["admin_correo"] = "adminB@conjunto.com"
    segunda = await cliente.post("/api/v1/business-units", headers=headers, data=payload)
    assert segunda.status_code == 409
    assert segunda.json()["codigo"] == "SLUG_DUPLICADO"


async def test_unidad_negocio_publica_inexistente_devuelve_404(cliente: AsyncClient) -> None:
    respuesta = await cliente.get("/api/v1/business-units/public/no-existe")
    assert respuesta.status_code == 404


async def test_login_de_unidad_inactiva_es_rechazado(
    cliente: AsyncClient, credenciales_admin_plataforma: dict[str, str]
) -> None:
    headers = {"Authorization": f"Bearer {await _token_plataforma(cliente, credenciales_admin_plataforma)}"}
    creacion = await cliente.post(
        "/api/v1/business-units",
        headers=headers,
        data={
            "nombre": "Conjunto Inactivo",
            "slug": "inactivo",
            "admin_nombre": "Admin Inactivo",
            "admin_correo": "admin@inactivo.com",
            "admin_password": "ClaveSegura123",
        },
    )
    unidad_id = creacion.json()["id"]

    await cliente.put(
        f"/api/v1/business-units/{unidad_id}",
        headers=headers,
        json={
            "nombre": "Conjunto Inactivo",
            "slug": "inactivo",
            "color_primario": "#000000",
            "color_secundario": "#ffffff",
            "activo": False,
        },
    )

    login = await cliente.post(
        "/api/v1/auth/login",
        json={
            "correo": "admin@inactivo.com",
            "password": "ClaveSegura123",
            "slug_unidad_negocio": "inactivo",
        },
    )
    assert login.status_code == 403
    assert login.json()["codigo"] == "UNIDAD_NEGOCIO_INACTIVA"


async def test_plataforma_puede_listar_y_restablecer_password_de_usuario(
    cliente: AsyncClient, credenciales_admin_plataforma: dict[str, str]
) -> None:
    headers = {"Authorization": f"Bearer {await _token_plataforma(cliente, credenciales_admin_plataforma)}"}
    creacion = await cliente.post(
        "/api/v1/business-units",
        headers=headers,
        data={
            "nombre": "Conjunto Recuperable",
            "slug": "recuperable",
            "admin_nombre": "Admin Recuperable",
            "admin_correo": "admin@recuperable.com",
            "admin_password": "ClaveOriginal123",
        },
    )
    unidad_id = creacion.json()["id"]

    listado = await cliente.get(f"/api/v1/business-units/{unidad_id}/users", headers=headers)
    assert listado.status_code == 200
    usuarios = listado.json()
    assert len(usuarios) == 1
    assert usuarios[0]["correo"] == "admin@recuperable.com"
    usuario_id = usuarios[0]["id"]

    restablecer = await cliente.post(
        f"/api/v1/business-units/{unidad_id}/users/{usuario_id}/reset-password", headers=headers
    )
    assert restablecer.status_code == 200, restablecer.text
    nueva_password = restablecer.json()["nueva_password"]
    assert nueva_password  # se generó una contraseña nueva
    assert nueva_password != "ClaveOriginal123"

    # La contraseña anterior ya no funciona
    login_viejo = await cliente.post(
        "/api/v1/auth/login",
        json={
            "correo": "admin@recuperable.com",
            "password": "ClaveOriginal123",
            "slug_unidad_negocio": "recuperable",
        },
    )
    assert login_viejo.status_code == 401

    # La contraseña nueva sí funciona
    login_nuevo = await cliente.post(
        "/api/v1/auth/login",
        json={
            "correo": "admin@recuperable.com",
            "password": nueva_password,
            "slug_unidad_negocio": "recuperable",
        },
    )
    assert login_nuevo.status_code == 200, login_nuevo.text


async def test_plataforma_puede_restablecer_con_password_personalizada(
    cliente: AsyncClient, credenciales_admin_plataforma: dict[str, str]
) -> None:
    headers = {"Authorization": f"Bearer {await _token_plataforma(cliente, credenciales_admin_plataforma)}"}
    creacion = await cliente.post(
        "/api/v1/business-units",
        headers=headers,
        data={
            "nombre": "Conjunto Personalizado",
            "slug": "personalizado",
            "admin_nombre": "Admin Personalizado",
            "admin_correo": "admin@personalizado.com",
            "admin_password": "ClaveOriginal123",
        },
    )
    unidad_id = creacion.json()["id"]

    listado = await cliente.get(f"/api/v1/business-units/{unidad_id}/users", headers=headers)
    usuario_id = listado.json()[0]["id"]

    restablecer = await cliente.post(
        f"/api/v1/business-units/{unidad_id}/users/{usuario_id}/reset-password",
        headers=headers,
        json={"nueva_password": "MiClaveElegida123"},
    )
    assert restablecer.status_code == 200, restablecer.text
    assert restablecer.json()["nueva_password"] == "MiClaveElegida123"

    login_nuevo = await cliente.post(
        "/api/v1/auth/login",
        json={
            "correo": "admin@personalizado.com",
            "password": "MiClaveElegida123",
            "slug_unidad_negocio": "personalizado",
        },
    )
    assert login_nuevo.status_code == 200, login_nuevo.text


async def test_restablecer_password_personalizada_muy_corta_es_rechazada(
    cliente: AsyncClient, credenciales_admin_plataforma: dict[str, str]
) -> None:
    headers = {"Authorization": f"Bearer {await _token_plataforma(cliente, credenciales_admin_plataforma)}"}
    creacion = await cliente.post(
        "/api/v1/business-units",
        headers=headers,
        data={
            "nombre": "Conjunto Corto",
            "slug": "corto",
            "admin_nombre": "Admin Corto",
            "admin_correo": "admin@corto.com",
            "admin_password": "ClaveOriginal123",
        },
    )
    unidad_id = creacion.json()["id"]
    listado = await cliente.get(f"/api/v1/business-units/{unidad_id}/users", headers=headers)
    usuario_id = listado.json()[0]["id"]

    restablecer = await cliente.post(
        f"/api/v1/business-units/{unidad_id}/users/{usuario_id}/reset-password",
        headers=headers,
        json={"nueva_password": "corta"},
    )
    assert restablecer.status_code == 422


async def test_super_admin_no_puede_restablecer_password_via_plataforma(
    cliente: AsyncClient, credenciales_super_admin: dict[str, str]
) -> None:
    token_resp = await cliente.post("/api/v1/auth/login", json=credenciales_super_admin)
    headers = {"Authorization": f"Bearer {token_resp.json()['access_token']}"}
    respuesta = await cliente.get("/api/v1/business-units/1/users", headers=headers)
    assert respuesta.status_code == 403
