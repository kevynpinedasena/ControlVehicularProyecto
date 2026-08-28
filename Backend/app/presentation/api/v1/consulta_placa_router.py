"""Endpoint de consulta rápida por placa. Accesible por Super Administrador y Vigilante."""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.use_cases.vehiculo_use_cases import ConsultarPlacaUseCase
from app.presentation.dependencies.autenticacion import UnidadNegocioActual, requerir_cualquier_rol
from app.presentation.dependencies.casos_uso import caso_uso_consultar_placa
from app.presentation.schemas.catalogo_schemas import TipoResidenteResponse, TipoVehiculoResponse
from app.presentation.schemas.vehiculo_schemas import ConsultaPlacaResponse

router = APIRouter(
    prefix="/vehicles",
    tags=["Consulta de placas"],
    dependencies=[Depends(requerir_cualquier_rol)],
)


@router.get("/plate/{placa}", response_model=ConsultaPlacaResponse)
async def consultar_placa(
    placa: str,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ConsultarPlacaUseCase, Depends(caso_uso_consultar_placa)],
) -> ConsultaPlacaResponse:
    resultado = await caso_uso.ejecutar(unidad_negocio_id, placa)
    return ConsultaPlacaResponse(
        registrado=resultado.registrado,
        placa=resultado.placa,
        mensaje=resultado.mensaje,
        tipo_vehiculo=(
            TipoVehiculoResponse(
                id=resultado.tipo_vehiculo.id,
                codigo=resultado.tipo_vehiculo.codigo,
                nombre=resultado.tipo_vehiculo.nombre,
            )
            if resultado.tipo_vehiculo
            else None
        ),
        torre=resultado.torre,
        apartamento=resultado.apartamento,
        tipo_residente=(
            TipoResidenteResponse(
                id=resultado.tipo_residente.id,
                codigo=resultado.tipo_residente.codigo,
                nombre=resultado.tipo_residente.nombre,
            )
            if resultado.tipo_residente
            else None
        ),
        estado=resultado.estado,
        telefono_1=resultado.telefono_1,
        telefono_2=resultado.telefono_2,
        parqueadero=resultado.parqueadero,
    )
