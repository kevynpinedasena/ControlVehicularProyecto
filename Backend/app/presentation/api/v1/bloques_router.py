"""Endpoints de gestión de bloques de parqueaderos. Consulta para Super Administrador y
Vigilante; creación/edición/eliminación restringida al Super Administrador de cada unidad."""
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.application.dto.parqueadero_dto import ActualizarBloqueDTO, CrearBloqueDTO
from app.application.use_cases.parqueadero_use_cases import (
    ActualizarBloqueUseCase,
    CrearBloqueUseCase,
    EliminarBloqueUseCase,
    ListarBloquesUseCase,
)
from app.domain.entities.bloque import Bloque
from app.presentation.dependencies.autenticacion import (
    UnidadNegocioActual,
    requerir_cualquier_rol,
    requerir_super_admin,
)
from app.presentation.dependencies.casos_uso import (
    caso_uso_actualizar_bloque,
    caso_uso_crear_bloque,
    caso_uso_eliminar_bloque,
    caso_uso_listar_bloques,
)
from app.presentation.schemas.parqueadero_schemas import (
    ActualizarBloqueRequest,
    BloqueResponse,
    CrearBloqueRequest,
)

router = APIRouter(prefix="/parking-blocks", tags=["Bloques de parqueaderos"])


def _a_response(bloque: Bloque) -> BloqueResponse:
    return BloqueResponse(id=bloque.id, nombre=bloque.nombre, codigo=bloque.codigo)


@router.get("", response_model=list[BloqueResponse], dependencies=[Depends(requerir_cualquier_rol)])
async def listar_bloques(
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ListarBloquesUseCase, Depends(caso_uso_listar_bloques)],
) -> list[BloqueResponse]:
    return [_a_response(b) for b in await caso_uso.ejecutar(unidad_negocio_id)]


@router.post(
    "",
    response_model=BloqueResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(requerir_super_admin)],
)
async def crear_bloque(
    datos: CrearBloqueRequest,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[CrearBloqueUseCase, Depends(caso_uso_crear_bloque)],
) -> BloqueResponse:
    bloque = await caso_uso.ejecutar(
        unidad_negocio_id, CrearBloqueDTO(nombre=datos.nombre, codigo=datos.codigo)
    )
    return _a_response(bloque)


@router.put(
    "/{bloque_id}", response_model=BloqueResponse, dependencies=[Depends(requerir_super_admin)]
)
async def actualizar_bloque(
    bloque_id: int,
    datos: ActualizarBloqueRequest,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ActualizarBloqueUseCase, Depends(caso_uso_actualizar_bloque)],
) -> BloqueResponse:
    bloque = await caso_uso.ejecutar(
        unidad_negocio_id, bloque_id, ActualizarBloqueDTO(nombre=datos.nombre, codigo=datos.codigo)
    )
    return _a_response(bloque)


@router.delete(
    "/{bloque_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(requerir_super_admin)]
)
async def eliminar_bloque(
    bloque_id: int,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[EliminarBloqueUseCase, Depends(caso_uso_eliminar_bloque)],
) -> None:
    await caso_uso.ejecutar(unidad_negocio_id, bloque_id)