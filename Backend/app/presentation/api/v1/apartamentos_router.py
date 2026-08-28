"""Endpoints de gestión de apartamentos. Consulta para Super Administrador y Vigilante;
creación/edición/eliminación restringida al Super Administrador de cada unidad."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.application.dto.ubicacion_dto import ActualizarApartamentoDTO, CrearApartamentoDTO
from app.application.use_cases.ubicacion_use_cases import (
    ActualizarApartamentoUseCase,
    CrearApartamentoUseCase,
    EliminarApartamentoUseCase,
    ListarApartamentosUseCase,
)
from app.domain.entities.apartamento import Apartamento
from app.presentation.dependencies.autenticacion import (
    UnidadNegocioActual,
    requerir_cualquier_rol,
    requerir_super_admin,
)
from app.presentation.dependencies.casos_uso import (
    caso_uso_actualizar_apartamento,
    caso_uso_crear_apartamento,
    caso_uso_eliminar_apartamento,
    caso_uso_listar_apartamentos,
)
from app.presentation.schemas.ubicacion_schemas import (
    ActualizarApartamentoRequest,
    ApartamentoResponse,
    CrearApartamentoRequest,
)

router = APIRouter(prefix="/apartments", tags=["Apartamentos"])


def _a_response(apartamento: Apartamento) -> ApartamentoResponse:
    return ApartamentoResponse(
        id=apartamento.id,
        torre_id=apartamento.torre_id,
        numero=apartamento.numero,
        activo=apartamento.activo,
    )


@router.get(
    "", response_model=list[ApartamentoResponse], dependencies=[Depends(requerir_cualquier_rol)]
)
async def listar_apartamentos(
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ListarApartamentosUseCase, Depends(caso_uso_listar_apartamentos)],
    torre_id: int | None = Query(default=None),
) -> list[ApartamentoResponse]:
    return [_a_response(a) for a in await caso_uso.ejecutar(unidad_negocio_id, torre_id=torre_id)]


@router.post(
    "",
    response_model=ApartamentoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(requerir_super_admin)],
)
async def crear_apartamento(
    datos: CrearApartamentoRequest,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[CrearApartamentoUseCase, Depends(caso_uso_crear_apartamento)],
) -> ApartamentoResponse:
    apartamento = await caso_uso.ejecutar(
        unidad_negocio_id, CrearApartamentoDTO(torre_id=datos.torre_id, numero=datos.numero)
    )
    return _a_response(apartamento)


@router.put(
    "/{apartamento_id}",
    response_model=ApartamentoResponse,
    dependencies=[Depends(requerir_super_admin)],
)
async def actualizar_apartamento(
    apartamento_id: int,
    datos: ActualizarApartamentoRequest,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ActualizarApartamentoUseCase, Depends(caso_uso_actualizar_apartamento)],
) -> ApartamentoResponse:
    apartamento = await caso_uso.ejecutar(
        unidad_negocio_id,
        apartamento_id,
        ActualizarApartamentoDTO(torre_id=datos.torre_id, numero=datos.numero, activo=datos.activo),
    )
    return _a_response(apartamento)


@router.delete(
    "/{apartamento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(requerir_super_admin)],
)
async def eliminar_apartamento(
    apartamento_id: int,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[EliminarApartamentoUseCase, Depends(caso_uso_eliminar_apartamento)],
) -> None:
    await caso_uso.ejecutar(unidad_negocio_id, apartamento_id)
