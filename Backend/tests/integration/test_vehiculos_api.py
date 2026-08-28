"""Pruebas de integración: registro de vehículos, placas duplicadas y consulta de placa."""
import pytest
from httpx import AsyncClient

from app.infrastructure.database.models import ApartamentoModel

pytestmark = pytest.mark.asyncio

_ID_TIPO_RESIDENTE = {"PROPIETARIO": 1, "ARRENDATARIO": 2}
_ID_TIPO_VEHICULO = {"CARRO": 1, "MOTO": 2}


async def _token_admin(cliente: AsyncClient, credenciales_super_admin: dict[str, str]) -> str:
    respuesta = await cliente.post("/api/v1/auth/login", json=credenciales_super_admin)
    return respuesta.json()["access_token"]


async def _crear_residente(
    cliente: AsyncClient,
    headers: dict[str, str],
    apartamento_id: int,
    tipo: str,
    documento: str,
    telefono_1: str | None = None,
) -> dict:
    respuesta = await cliente.post(
        "/api/v1/residents",
        json={
            "nombre": "Residente de Prueba",
            "documento": documento,
            "tipo_residente_id": _ID_TIPO_RESIDENTE[tipo],
            "apartamento_id": apartamento_id,
            "telefono_1": telefono_1,
        },
        headers=headers,
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


async def test_registrar_placa_duplicada_es_rechazado(
    cliente: AsyncClient,
    credenciales_super_admin: dict[str, str],
    torre_y_apartamento: ApartamentoModel,
) -> None:
    headers = {"Authorization": f"Bearer {await _token_admin(cliente, credenciales_super_admin)}"}
    residente = await _crear_residente(
        cliente, headers, torre_y_apartamento.id, "PROPIETARIO", "1000001"
    )

    primera = await cliente.post(
        "/api/v1/vehicles",
        json={"placa": "abc123", "tipo_vehiculo_id": 1, "residente_id": residente["id"]},
        headers=headers,
    )
    assert primera.status_code == 201

    segunda = await cliente.post(
        "/api/v1/vehicles",
        json={"placa": "ABC123", "tipo_vehiculo_id": 2, "residente_id": residente["id"]},
        headers=headers,
    )
    assert segunda.status_code == 409
    assert segunda.json()["codigo"] == "PLACA_DUPLICADA"


async def test_consultar_placa_registrada_devuelve_ubicacion(
    cliente: AsyncClient,
    credenciales_super_admin: dict[str, str],
    torre_y_apartamento: ApartamentoModel,
) -> None:
    headers = {"Authorization": f"Bearer {await _token_admin(cliente, credenciales_super_admin)}"}
    residente = await _crear_residente(
        cliente, headers, torre_y_apartamento.id, "ARRENDATARIO", "1000002", telefono_1="3001112233"
    )
    await cliente.post(
        "/api/v1/vehicles",
        json={"placa": "XYZ789", "tipo_vehiculo_id": 1, "residente_id": residente["id"]},
        headers=headers,
    )

    respuesta = await cliente.get("/api/v1/vehicles/plate/xyz789", headers=headers)
    datos = respuesta.json()

    assert respuesta.status_code == 200
    assert datos["registrado"] is True
    assert datos["placa"] == "XYZ789"
    assert datos["tipo_vehiculo"]["codigo"] == "CARRO"
    assert datos["tipo_residente"]["codigo"] == "ARRENDATARIO"
    assert datos["telefono_1"] == "3001112233"
    assert datos["torre"] == "Torre 1"
    assert datos["apartamento"] == "101"


async def test_consultar_placa_no_registrada(
    cliente: AsyncClient, credenciales_super_admin: dict[str, str]
) -> None:
    headers = {"Authorization": f"Bearer {await _token_admin(cliente, credenciales_super_admin)}"}
    respuesta = await cliente.get("/api/v1/vehicles/plate/ZZZ999", headers=headers)

    assert respuesta.status_code == 200
    assert respuesta.json()["registrado"] is False


async def test_propietario_no_puede_registrar_dos_carros_via_api(
    cliente: AsyncClient,
    credenciales_super_admin: dict[str, str],
    torre_y_apartamento: ApartamentoModel,
) -> None:
    headers = {"Authorization": f"Bearer {await _token_admin(cliente, credenciales_super_admin)}"}
    residente = await _crear_residente(
        cliente, headers, torre_y_apartamento.id, "PROPIETARIO", "1000003"
    )
    await cliente.post(
        "/api/v1/vehicles",
        json={"placa": "AAA111", "tipo_vehiculo_id": 1, "residente_id": residente["id"]},
        headers=headers,
    )

    respuesta = await cliente.post(
        "/api/v1/vehicles",
        json={"placa": "BBB222", "tipo_vehiculo_id": 1, "residente_id": residente["id"]},
        headers=headers,
    )
    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "REGLA_VEHICULO_INVALIDA"