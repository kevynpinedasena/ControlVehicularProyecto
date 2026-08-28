"""Endpoint de solo lectura para el catálogo global de tipos de vehículo."""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.use_cases.tipo_use_cases import ListarTiposVehiculoUseCase
from app.presentation.dependencies.autenticacion import requerir_cualquier_rol
from app.presentation.dependencies.casos_uso import caso_uso_listar_tipos_vehiculo
from app.presentation.schemas.catalogo_schemas import TipoVehiculoResponse

router = APIRouter(
    prefix="/vehicle-types",
    tags=["Catálogos"],
    dependencies=[Depends(requerir_cualquier_rol)],
)


@router.get("", response_model=list[TipoVehiculoResponse])
async def listar_tipos_vehiculo(
    caso_uso: Annotated[ListarTiposVehiculoUseCase, Depends(caso_uso_listar_tipos_vehiculo)],
) -> list[TipoVehiculoResponse]:
    tipos = await caso_uso.ejecutar()
    return [TipoVehiculoResponse(id=t.id, codigo=t.codigo, nombre=t.nombre) for t in tipos]