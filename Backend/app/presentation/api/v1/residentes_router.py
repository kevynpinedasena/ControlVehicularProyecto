"""Endpoints de gestión de residentes. Consulta para Super Administrador y Vigilante;
creación/edición/eliminación restringida al Super Administrador de cada unidad."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.application.dto.residente_dto import ActualizarResidenteDTO, CrearResidenteDTO
from app.application.use_cases.residente_use_cases import (
    ActualizarResidenteUseCase,
    CrearResidenteUseCase,
    EliminarResidenteUseCase,
    ListarResidentesUseCase,
    ObtenerResidenteUseCase,
)
from app.domain.entities.residente import Residente
from app.presentation.dependencies.autenticacion import (
    UnidadNegocioActual,
    requerir_cualquier_rol,
    requerir_super_admin,
)
from app.presentation.dependencies.casos_uso import (
    caso_uso_actualizar_residente,
    caso_uso_crear_residente,
    caso_uso_eliminar_residente,
    caso_uso_listar_residentes,
    caso_uso_obtener_residente,
)
from app.presentation.schemas.catalogo_schemas import TipoResidenteResponse, TipoVehiculoResponse
from app.presentation.schemas.residente_schemas import (
    ActualizarResidenteRequest,
    CrearResidenteRequest,
    ResidenteResponse,
)
from app.presentation.schemas.vehiculo_schemas import VehiculoResponse

router = APIRouter(prefix="/residents", tags=["Residentes"])


def _a_response(residente: Residente) -> ResidenteResponse:
    return ResidenteResponse(
        id=residente.id,
        nombre=residente.nombre,
        documento=residente.documento,
        tipo_residente=TipoResidenteResponse(
            id=residente.tipo_residente.id,
            codigo=residente.tipo_residente.codigo,
            nombre=residente.tipo_residente.nombre,
        ),
        apartamento_id=residente.apartamento_id,
        telefono_1=residente.telefono_1,
        telefono_2=residente.telefono_2,
        activo=residente.activo,
        created_at=residente.created_at,
        updated_at=residente.updated_at,
        vehiculos=[
            VehiculoResponse(
                id=v.id,
                placa=str(v.placa),
                tipo_vehiculo=TipoVehiculoResponse(
                    id=v.tipo_vehiculo.id, codigo=v.tipo_vehiculo.codigo, nombre=v.tipo_vehiculo.nombre
                ),
                residente_id=v.residente_id,
                parqueadero_id=v.parqueadero_id,
                activo=v.activo,
                created_at=v.created_at,
                updated_at=v.updated_at,
            )
            for v in residente.vehiculos
        ],
    )


@router.get("", response_model=list[ResidenteResponse], dependencies=[Depends(requerir_cualquier_rol)])
async def listar_residentes(
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ListarResidentesUseCase, Depends(caso_uso_listar_residentes)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    busqueda: str | None = Query(default=None, description="Busca por nombre o documento"),
) -> list[ResidenteResponse]:
    residentes = await caso_uso.ejecutar(unidad_negocio_id, skip=skip, limit=limit, busqueda=busqueda)
    return [_a_response(r) for r in residentes]


@router.post(
    "",
    response_model=ResidenteResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(requerir_super_admin)],
)
async def crear_residente(
    datos: CrearResidenteRequest,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[CrearResidenteUseCase, Depends(caso_uso_crear_residente)],
) -> ResidenteResponse:
    residente = await caso_uso.ejecutar(
        unidad_negocio_id,
        CrearResidenteDTO(
            nombre=datos.nombre,
            documento=datos.documento,
            tipo_residente_id=datos.tipo_residente_id,
            apartamento_id=datos.apartamento_id,
            telefono_1=datos.telefono_1,
            telefono_2=datos.telefono_2,
        ),
    )
    return _a_response(residente)


@router.get(
    "/{residente_id}", response_model=ResidenteResponse, dependencies=[Depends(requerir_cualquier_rol)]
)
async def obtener_residente(
    residente_id: int,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ObtenerResidenteUseCase, Depends(caso_uso_obtener_residente)],
) -> ResidenteResponse:
    return _a_response(await caso_uso.ejecutar(unidad_negocio_id, residente_id))


@router.put(
    "/{residente_id}", response_model=ResidenteResponse, dependencies=[Depends(requerir_super_admin)]
)
async def actualizar_residente(
    residente_id: int,
    datos: ActualizarResidenteRequest,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ActualizarResidenteUseCase, Depends(caso_uso_actualizar_residente)],
) -> ResidenteResponse:
    residente = await caso_uso.ejecutar(
        unidad_negocio_id,
        residente_id,
        ActualizarResidenteDTO(
            nombre=datos.nombre,
            documento=datos.documento,
            tipo_residente_id=datos.tipo_residente_id,
            apartamento_id=datos.apartamento_id,
            activo=datos.activo,
            telefono_1=datos.telefono_1,
            telefono_2=datos.telefono_2,
        ),
    )
    return _a_response(residente)


@router.delete(
    "/{residente_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(requerir_super_admin)]
)
async def eliminar_residente(
    residente_id: int,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[EliminarResidenteUseCase, Depends(caso_uso_eliminar_residente)],
) -> None:
    await caso_uso.ejecutar(unidad_negocio_id, residente_id)
