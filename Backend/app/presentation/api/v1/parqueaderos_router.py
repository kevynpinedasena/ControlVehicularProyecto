"""Endpoints de gestión de parqueaderos. Consulta para Super Administrador y Vigilante;
creación/edición/eliminación restringida al Super Administrador de cada unidad."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.application.dto.parqueadero_dto import (
    ActualizarParqueaderoDTO,
    CrearParqueaderoDTO,
    ParqueaderoConOcupacionDTO,
)
from app.application.use_cases.parqueadero_use_cases import (
    ActualizarParqueaderoUseCase,
    CrearParqueaderoUseCase,
    EliminarParqueaderoUseCase,
    ListarParqueaderosUseCase,
)
from app.presentation.dependencies.autenticacion import (
    UnidadNegocioActual,
    requerir_cualquier_rol,
    requerir_super_admin,
)
from app.presentation.dependencies.casos_uso import (
    caso_uso_actualizar_parqueadero,
    caso_uso_crear_parqueadero,
    caso_uso_eliminar_parqueadero,
    caso_uso_listar_parqueaderos,
)
from app.presentation.schemas.catalogo_schemas import TipoVehiculoResponse
from app.presentation.schemas.parqueadero_schemas import (
    ActualizarParqueaderoRequest,
    CrearParqueaderoRequest,
    ParqueaderoResponse,
)

router = APIRouter(prefix="/parking-spots", tags=["Parqueaderos"])


def _a_response(dto: ParqueaderoConOcupacionDTO) -> ParqueaderoResponse:
    p = dto.parqueadero
    return ParqueaderoResponse(
        id=p.id,
        bloque_id=p.bloque_id,
        numero=p.numero,
        tipo_espacio=p.tipo_espacio,
        tipo_vehiculo=TipoVehiculoResponse(
            id=p.tipo_vehiculo.id, codigo=p.tipo_vehiculo.codigo, nombre=p.tipo_vehiculo.nombre
        ),
        capacidad=p.capacidad,
        propietario_residente_id=p.propietario_residente_id,
        vehiculos_asignados=dto.vehiculos_asignados,
        activo=p.activo,
    )


@router.get("", response_model=list[ParqueaderoResponse], dependencies=[Depends(requerir_cualquier_rol)])
async def listar_parqueaderos(
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ListarParqueaderosUseCase, Depends(caso_uso_listar_parqueaderos)],
    bloque_id: int | None = Query(default=None),
) -> list[ParqueaderoResponse]:
    return [_a_response(p) for p in await caso_uso.ejecutar(unidad_negocio_id, bloque_id=bloque_id)]


@router.post(
    "",
    response_model=ParqueaderoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(requerir_super_admin)],
)
async def crear_parqueadero(
    datos: CrearParqueaderoRequest,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[CrearParqueaderoUseCase, Depends(caso_uso_crear_parqueadero)],
) -> ParqueaderoResponse:
    resultado = await caso_uso.ejecutar(
        unidad_negocio_id,
        CrearParqueaderoDTO(
            bloque_id=datos.bloque_id,
            numero=datos.numero,
            tipo_espacio=datos.tipo_espacio,
            tipo_vehiculo_id=datos.tipo_vehiculo_id,
            capacidad=datos.capacidad,
            propietario_residente_id=datos.propietario_residente_id,
        ),
    )
    return _a_response(resultado)


@router.put(
    "/{parqueadero_id}", response_model=ParqueaderoResponse, dependencies=[Depends(requerir_super_admin)]
)
async def actualizar_parqueadero(
    parqueadero_id: int,
    datos: ActualizarParqueaderoRequest,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ActualizarParqueaderoUseCase, Depends(caso_uso_actualizar_parqueadero)],
) -> ParqueaderoResponse:
    resultado = await caso_uso.ejecutar(
        unidad_negocio_id,
        parqueadero_id,
        ActualizarParqueaderoDTO(
            bloque_id=datos.bloque_id,
            numero=datos.numero,
            tipo_espacio=datos.tipo_espacio,
            tipo_vehiculo_id=datos.tipo_vehiculo_id,
            capacidad=datos.capacidad,
            activo=datos.activo,
            propietario_residente_id=datos.propietario_residente_id,
        ),
    )
    return _a_response(resultado)


@router.delete(
    "/{parqueadero_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(requerir_super_admin)],
)
async def eliminar_parqueadero(
    parqueadero_id: int,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[EliminarParqueaderoUseCase, Depends(caso_uso_eliminar_parqueadero)],
) -> None:
    await caso_uso.ejecutar(unidad_negocio_id, parqueadero_id)