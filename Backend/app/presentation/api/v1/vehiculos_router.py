"""Endpoints de gestión (CRUD) de vehículos. Restringido al Super Administrador de cada unidad."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.application.dto.vehiculo_dto import (
    ActualizarVehiculoDTO,
    AsignarParqueaderoVehiculoDTO,
    CrearVehiculoDTO,
)
from app.application.use_cases.vehiculo_use_cases import (
    ActualizarVehiculoUseCase,
    AsignarParqueaderoVehiculoUseCase,
    EliminarVehiculoUseCase,
    ListarVehiculosUseCase,
    ObtenerVehiculoUseCase,
    RegistrarVehiculoUseCase,
)
from app.domain.entities.vehiculo import Vehiculo
from app.presentation.dependencies.autenticacion import UnidadNegocioActual, requerir_super_admin
from app.presentation.dependencies.casos_uso import (
    caso_uso_actualizar_vehiculo,
    caso_uso_asignar_parqueadero_vehiculo,
    caso_uso_eliminar_vehiculo,
    caso_uso_listar_vehiculos,
    caso_uso_obtener_vehiculo,
    caso_uso_registrar_vehiculo,
)
from app.presentation.schemas.catalogo_schemas import TipoVehiculoResponse
from app.presentation.schemas.parqueadero_schemas import AsignarParqueaderoRequest
from app.presentation.schemas.vehiculo_schemas import (
    ActualizarVehiculoRequest,
    CrearVehiculoRequest,
    VehiculoResponse,
)

router = APIRouter(
    prefix="/vehicles",
    tags=["Vehículos"],
    dependencies=[Depends(requerir_super_admin)],
)


def _a_response(vehiculo: Vehiculo) -> VehiculoResponse:
    return VehiculoResponse(
        id=vehiculo.id,
        placa=str(vehiculo.placa),
        tipo_vehiculo=TipoVehiculoResponse(
            id=vehiculo.tipo_vehiculo.id,
            codigo=vehiculo.tipo_vehiculo.codigo,
            nombre=vehiculo.tipo_vehiculo.nombre,
        ),
        residente_id=vehiculo.residente_id,
        parqueadero_id=vehiculo.parqueadero_id,
        activo=vehiculo.activo,
        created_at=vehiculo.created_at,
        updated_at=vehiculo.updated_at,
    )


@router.get("", response_model=list[VehiculoResponse])
async def listar_vehiculos(
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ListarVehiculosUseCase, Depends(caso_uso_listar_vehiculos)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    busqueda: str | None = Query(default=None, description="Busca por placa"),
    parqueadero_id: int | None = Query(default=None),
) -> list[VehiculoResponse]:
    vehiculos = await caso_uso.ejecutar(
        unidad_negocio_id, skip=skip, limit=limit, busqueda=busqueda, parqueadero_id=parqueadero_id
    )
    return [_a_response(v) for v in vehiculos]


@router.post("", response_model=VehiculoResponse, status_code=status.HTTP_201_CREATED)
async def registrar_vehiculo(
    datos: CrearVehiculoRequest,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[RegistrarVehiculoUseCase, Depends(caso_uso_registrar_vehiculo)],
) -> VehiculoResponse:
    vehiculo = await caso_uso.ejecutar(
        unidad_negocio_id,
        CrearVehiculoDTO(
            placa=datos.placa,
            tipo_vehiculo_id=datos.tipo_vehiculo_id,
            residente_id=datos.residente_id,
        ),
    )
    return _a_response(vehiculo)


@router.get("/{vehiculo_id}", response_model=VehiculoResponse)
async def obtener_vehiculo(
    vehiculo_id: int,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ObtenerVehiculoUseCase, Depends(caso_uso_obtener_vehiculo)],
) -> VehiculoResponse:
    return _a_response(await caso_uso.ejecutar(unidad_negocio_id, vehiculo_id))


@router.put("/{vehiculo_id}", response_model=VehiculoResponse)
async def actualizar_vehiculo(
    vehiculo_id: int,
    datos: ActualizarVehiculoRequest,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ActualizarVehiculoUseCase, Depends(caso_uso_actualizar_vehiculo)],
) -> VehiculoResponse:
    vehiculo = await caso_uso.ejecutar(
        unidad_negocio_id,
        vehiculo_id,
        ActualizarVehiculoDTO(
            placa=datos.placa, tipo_vehiculo_id=datos.tipo_vehiculo_id, activo=datos.activo
        ),
    )
    return _a_response(vehiculo)


@router.put("/{vehiculo_id}/parking-spot", response_model=VehiculoResponse)
async def asignar_parqueadero_vehiculo(
    vehiculo_id: int,
    datos: AsignarParqueaderoRequest,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[
        AsignarParqueaderoVehiculoUseCase, Depends(caso_uso_asignar_parqueadero_vehiculo)
    ],
) -> VehiculoResponse:
    vehiculo = await caso_uso.ejecutar(
        unidad_negocio_id, vehiculo_id, AsignarParqueaderoVehiculoDTO(parqueadero_id=datos.parqueadero_id)
    )
    return _a_response(vehiculo)


@router.delete("/{vehiculo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_vehiculo(
    vehiculo_id: int,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[EliminarVehiculoUseCase, Depends(caso_uso_eliminar_vehiculo)],
) -> None:
    await caso_uso.ejecutar(unidad_negocio_id, vehiculo_id)
