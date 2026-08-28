"""Endpoints de gestión de torres. Consulta para Super Administrador y Vigilante;
creación/edición/eliminación restringida al Super Administrador de cada unidad."""
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.dto.ubicacion_dto import ActualizarTorreDTO, CrearTorreDTO
from app.application.use_cases.ubicacion_use_cases import (
    ActualizarTorreUseCase,
    CrearTorreUseCase,
    EliminarTorreUseCase,
    ListarTorresUseCase,
)
from app.domain.entities.torre import Torre
from app.presentation.dependencies.autenticacion import (
    UnidadNegocioActual,
    requerir_cualquier_rol,
    requerir_super_admin,
)
from app.presentation.dependencies.casos_uso import (
    caso_uso_actualizar_torre,
    caso_uso_crear_torre,
    caso_uso_eliminar_torre,
    caso_uso_listar_torres,
)
from app.presentation.schemas.ubicacion_schemas import (
    ActualizarTorreRequest,
    CrearTorreRequest,
    TorreResponse,
)

router = APIRouter(prefix="/towers", tags=["Torres"])


def _a_response(torre: Torre) -> TorreResponse:
    return TorreResponse(id=torre.id, nombre=torre.nombre, codigo=torre.codigo)


@router.get("", response_model=list[TorreResponse], dependencies=[Depends(requerir_cualquier_rol)])
async def listar_torres(
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ListarTorresUseCase, Depends(caso_uso_listar_torres)],
) -> list[TorreResponse]:
    return [_a_response(t) for t in await caso_uso.ejecutar(unidad_negocio_id)]


@router.post(
    "",
    response_model=TorreResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(requerir_super_admin)],
)
async def crear_torre(
    datos: CrearTorreRequest,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[CrearTorreUseCase, Depends(caso_uso_crear_torre)],
) -> TorreResponse:
    torre = await caso_uso.ejecutar(
        unidad_negocio_id, CrearTorreDTO(nombre=datos.nombre, codigo=datos.codigo)
    )
    return _a_response(torre)


@router.put(
    "/{torre_id}", response_model=TorreResponse, dependencies=[Depends(requerir_super_admin)]
)
async def actualizar_torre(
    torre_id: int,
    datos: ActualizarTorreRequest,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ActualizarTorreUseCase, Depends(caso_uso_actualizar_torre)],
) -> TorreResponse:
    torre = await caso_uso.ejecutar(
        unidad_negocio_id, torre_id, ActualizarTorreDTO(nombre=datos.nombre, codigo=datos.codigo)
    )
    return _a_response(torre)


@router.delete(
    "/{torre_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(requerir_super_admin)]
)
async def eliminar_torre(
    torre_id: int,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[EliminarTorreUseCase, Depends(caso_uso_eliminar_torre)],
) -> None:
    await caso_uso.ejecutar(unidad_negocio_id, torre_id)
