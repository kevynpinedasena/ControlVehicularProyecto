"""Endpoint de solo lectura para el catálogo global de tipos de residente."""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.use_cases.tipo_use_cases import ListarTiposResidenteUseCase
from app.presentation.dependencies.autenticacion import requerir_cualquier_rol
from app.presentation.dependencies.casos_uso import caso_uso_listar_tipos_residente
from app.presentation.schemas.catalogo_schemas import TipoResidenteResponse

router = APIRouter(
    prefix="/resident-types",
    tags=["Catálogos"],
    dependencies=[Depends(requerir_cualquier_rol)],
)


@router.get("", response_model=list[TipoResidenteResponse])
async def listar_tipos_residente(
    caso_uso: Annotated[ListarTiposResidenteUseCase, Depends(caso_uso_listar_tipos_residente)],
) -> list[TipoResidenteResponse]:
    tipos = await caso_uso.ejecutar()
    return [TipoResidenteResponse(id=t.id, codigo=t.codigo, nombre=t.nombre) for t in tipos]