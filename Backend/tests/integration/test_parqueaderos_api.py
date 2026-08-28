"""Pruebas de integración: bloques, parqueaderos y asignación de vehículos a parqueaderos."""
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
    cliente: AsyncClient, headers: dict[str, str], apartamento_id: int, tipo: str, documento: str
) -> dict:
    respuesta = await cliente.post(
        "/api/v1/residents",
        json={
            "nombre": "Residente de Prueba",
            "documento": documento,
            "tipo_residente_id": _ID_TIPO_RESIDENTE[tipo],
            "apartamento_id": apartamento_id,
        },
        headers=headers,
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


async def _crear_vehiculo(cliente: AsyncClient, headers: dict[str, str], placa: str, tipo: str, residente_id: int) -> dict:
    respuesta = await cliente.post(
        "/api/v1/vehicles",
        json={"placa": placa, "tipo_vehiculo_id": _ID_TIPO_VEHICULO[tipo], "residente_id": residente_id},
        headers=headers,
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


async def _crear_bloque(cliente: AsyncClient, headers: dict[str, str], nombre: str, codigo: str) -> dict:
    respuesta = await cliente.post(
        "/api/v1/parking-blocks", json={"nombre": nombre, "codigo": codigo}, headers=headers
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


async def test_crear_bloque_y_parqueadero_comunal(
    cliente: AsyncClient, credenciales_super_admin: dict[str, str]
) -> None:
    headers = {"Authorization": f"Bearer {await _token_admin(cliente, credenciales_super_admin)}"}
    bloque = await _crear_bloque(cliente, headers, "Subterráneo", "SUB")

    respuesta = await cliente.post(
        "/api/v1/parking-spots",
        json={
            "bloque_id": bloque["id"],
            "numero": "1",
            "tipo_espacio": "COMUNAL",
            "tipo_vehiculo_id": _ID_TIPO_VEHICULO["MOTO"],
            "capacidad": 3,
        },
        headers=headers,
    )
    assert respuesta.status_code == 201, respuesta.text
    parqueadero = respuesta.json()
    assert parqueadero["tipo_espacio"] == "COMUNAL"
    assert parqueadero["propietario_residente_id"] is None
    assert parqueadero["capacidad"] == 3
    assert parqueadero["vehiculos_asignados"] == 0


async def test_parqueadero_privado_requiere_propietario_valido(
    cliente: AsyncClient,
    credenciales_super_admin: dict[str, str],
    torre_y_apartamento: ApartamentoModel,
) -> None:
    headers = {"Authorization": f"Bearer {await _token_admin(cliente, credenciales_super_admin)}"}
    bloque = await _crear_bloque(cliente, headers, "Arriba", "ARR")

    # Sin propietario_residente_id -> error
    sin_dueno = await cliente.post(
        "/api/v1/parking-spots",
        json={
            "bloque_id": bloque["id"],
            "numero": "1",
            "tipo_espacio": "PRIVADO",
            "tipo_vehiculo_id": _ID_TIPO_VEHICULO["CARRO"],
            "capacidad": 1,
        },
        headers=headers,
    )
    assert sin_dueno.status_code == 400
    assert sin_dueno.json()["codigo"] == "PROPIETARIO_INVALIDO"

    # Dueño arrendatario -> error
    arrendatario = await _crear_residente(cliente, headers, torre_y_apartamento.id, "ARRENDATARIO", "700001")
    dueno_invalido = await cliente.post(
        "/api/v1/parking-spots",
        json={
            "bloque_id": bloque["id"],
            "numero": "1",
            "tipo_espacio": "PRIVADO",
            "tipo_vehiculo_id": _ID_TIPO_VEHICULO["CARRO"],
            "capacidad": 1,
            "propietario_residente_id": arrendatario["id"],
        },
        headers=headers,
    )
    assert dueno_invalido.status_code == 400
    assert dueno_invalido.json()["codigo"] == "PROPIETARIO_INVALIDO"

    # Dueño propietario -> éxito
    propietario = await _crear_residente(cliente, headers, torre_y_apartamento.id, "PROPIETARIO", "700002")
    valido = await cliente.post(
        "/api/v1/parking-spots",
        json={
            "bloque_id": bloque["id"],
            "numero": "1",
            "tipo_espacio": "PRIVADO",
            "tipo_vehiculo_id": _ID_TIPO_VEHICULO["CARRO"],
            "capacidad": 1,
            "propietario_residente_id": propietario["id"],
        },
        headers=headers,
    )
    assert valido.status_code == 201, valido.text
    assert valido.json()["propietario_residente_id"] == propietario["id"]


async def test_asignar_vehiculo_respeta_tipo_y_capacidad(
    cliente: AsyncClient,
    credenciales_super_admin: dict[str, str],
    torre_y_apartamento: ApartamentoModel,
) -> None:
    headers = {"Authorization": f"Bearer {await _token_admin(cliente, credenciales_super_admin)}"}
    bloque = await _crear_bloque(cliente, headers, "Bloque Motos", "BMT")
    parqueadero = (
        await cliente.post(
            "/api/v1/parking-spots",
            json={
                "bloque_id": bloque["id"],
                "numero": "1",
                "tipo_espacio": "COMUNAL",
                "tipo_vehiculo_id": _ID_TIPO_VEHICULO["MOTO"],
                "capacidad": 1,
            },
            headers=headers,
        )
    ).json()

    propietario = await _crear_residente(cliente, headers, torre_y_apartamento.id, "PROPIETARIO", "700010")
    moto = await _crear_vehiculo(cliente, headers, "MOT001", "MOTO", propietario["id"])
    carro = await _crear_vehiculo(cliente, headers, "CAR001", "CARRO", propietario["id"])

    # Tipo incompatible: el parqueadero solo admite motos
    incompatible = await cliente.put(
        f"/api/v1/vehicles/{carro['id']}/parking-spot",
        json={"parqueadero_id": parqueadero["id"]},
        headers=headers,
    )
    assert incompatible.status_code == 400
    assert incompatible.json()["codigo"] == "TIPO_VEHICULO_INCOMPATIBLE"

    # Asignación válida
    asignado = await cliente.put(
        f"/api/v1/vehicles/{moto['id']}/parking-spot",
        json={"parqueadero_id": parqueadero["id"]},
        headers=headers,
    )
    assert asignado.status_code == 200, asignado.text
    assert asignado.json()["parqueadero_id"] == parqueadero["id"]

    listado = await cliente.get(
        f"/api/v1/parking-spots?bloque_id={bloque['id']}", headers=headers
    )
    assert listado.json()[0]["vehiculos_asignados"] == 1

    vehiculos_del_spot = await cliente.get(
        f"/api/v1/vehicles?parqueadero_id={parqueadero['id']}", headers=headers
    )
    assert len(vehiculos_del_spot.json()) == 1
    assert vehiculos_del_spot.json()[0]["placa"] == "MOT001"

    # Capacidad llena: otra moto no cabe (de otro residente, para no chocar con el
    # límite de máx. 2 vehículos por propietario)
    propietario2 = await _crear_residente(cliente, headers, torre_y_apartamento.id, "PROPIETARIO", "700011")
    moto2 = await _crear_vehiculo(cliente, headers, "MOT002", "MOTO", propietario2["id"])
    lleno = await cliente.put(
        f"/api/v1/vehicles/{moto2['id']}/parking-spot",
        json={"parqueadero_id": parqueadero["id"]},
        headers=headers,
    )
    assert lleno.status_code == 400
    assert lleno.json()["codigo"] == "PARQUEADERO_LLENO"

    # Desasignar ("sacarla de ahí")
    desasignado = await cliente.put(
        f"/api/v1/vehicles/{moto['id']}/parking-spot", json={"parqueadero_id": None}, headers=headers
    )
    assert desasignado.status_code == 200
    assert desasignado.json()["parqueadero_id"] is None

    # Ahora sí cabe la segunda moto ("cambiar para otro" reutiliza el mismo endpoint)
    reasignado = await cliente.put(
        f"/api/v1/vehicles/{moto2['id']}/parking-spot",
        json={"parqueadero_id": parqueadero["id"]},
        headers=headers,
    )
    assert reasignado.status_code == 200, reasignado.text


async def test_codigo_bloque_y_numero_parqueadero_duplicados(
    cliente: AsyncClient, credenciales_super_admin: dict[str, str]
) -> None:
    headers = {"Authorization": f"Bearer {await _token_admin(cliente, credenciales_super_admin)}"}
    await _crear_bloque(cliente, headers, "Bloque Uno", "DUP")

    duplicado = await cliente.post(
        "/api/v1/parking-blocks", json={"nombre": "Otro nombre", "codigo": "DUP"}, headers=headers
    )
    assert duplicado.status_code == 409
    assert duplicado.json()["codigo"] == "CODIGO_BLOQUE_DUPLICADO"

    bloque = await _crear_bloque(cliente, headers, "Bloque Dos", "DUP2")
    await cliente.post(
        "/api/v1/parking-spots",
        json={
            "bloque_id": bloque["id"],
            "numero": "5",
            "tipo_espacio": "COMUNAL",
            "tipo_vehiculo_id": _ID_TIPO_VEHICULO["CARRO"],
            "capacidad": 1,
        },
        headers=headers,
    )
    numero_duplicado = await cliente.post(
        "/api/v1/parking-spots",
        json={
            "bloque_id": bloque["id"],
            "numero": "5",
            "tipo_espacio": "COMUNAL",
            "tipo_vehiculo_id": _ID_TIPO_VEHICULO["CARRO"],
            "capacidad": 1,
        },
        headers=headers,
    )
    assert numero_duplicado.status_code == 409
    assert numero_duplicado.json()["codigo"] == "PARQUEADERO_DUPLICADO"


async def test_editar_vehiculo_no_borra_su_parqueadero_asignado(
    cliente: AsyncClient,
    credenciales_super_admin: dict[str, str],
    torre_y_apartamento: ApartamentoModel,
) -> None:
    """Regresión: actualizar placa/tipo/estado de un vehículo no debe desasignar su parqueadero."""
    headers = {"Authorization": f"Bearer {await _token_admin(cliente, credenciales_super_admin)}"}
    bloque = await _crear_bloque(cliente, headers, "Bloque Regresión", "REG")
    parqueadero = (
        await cliente.post(
            "/api/v1/parking-spots",
            json={
                "bloque_id": bloque["id"],
                "numero": "1",
                "tipo_espacio": "COMUNAL",
                "tipo_vehiculo_id": _ID_TIPO_VEHICULO["CARRO"],
                "capacidad": 1,
            },
            headers=headers,
        )
    ).json()

    propietario = await _crear_residente(cliente, headers, torre_y_apartamento.id, "PROPIETARIO", "700099")
    vehiculo = await _crear_vehiculo(cliente, headers, "REG001", "CARRO", propietario["id"])
    await cliente.put(
        f"/api/v1/vehicles/{vehiculo['id']}/parking-spot",
        json={"parqueadero_id": parqueadero["id"]},
        headers=headers,
    )

    actualizado = await cliente.put(
        f"/api/v1/vehicles/{vehiculo['id']}",
        json={"placa": "REG001", "tipo_vehiculo_id": _ID_TIPO_VEHICULO["CARRO"], "activo": True},
        headers=headers,
    )
    assert actualizado.status_code == 200, actualizado.text
    assert actualizado.json()["parqueadero_id"] == parqueadero["id"]