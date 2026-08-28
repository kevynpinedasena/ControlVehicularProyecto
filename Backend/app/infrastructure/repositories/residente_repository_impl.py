from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.residente import Residente
from app.domain.entities.tipo_residente import TipoResidente
from app.domain.entities.tipo_vehiculo import TipoVehiculo
from app.domain.entities.vehiculo import Vehiculo
from app.domain.repositories.residente_repository import IResidenteRepository
from app.domain.value_objects.placa import Placa
from app.infrastructure.database.models import ResidenteModel, VehiculoModel


def _vehiculo_a_entidad(modelo: VehiculoModel) -> Vehiculo:
    return Vehiculo(
        id=modelo.id,
        placa=Placa(modelo.placa),
        tipo_vehiculo=TipoVehiculo(
            id=modelo.tipo_vehiculo_id,
            codigo=modelo.tipo_vehiculo_rel.codigo,
            nombre=modelo.tipo_vehiculo_rel.nombre,
        ),
        residente_id=modelo.residente_id,
        unidad_negocio_id=modelo.unidad_negocio_id,
        parqueadero_id=modelo.parqueadero_id,
        activo=modelo.activo,
        created_at=modelo.created_at,
        updated_at=modelo.updated_at,
    )


def _a_entidad(modelo: ResidenteModel) -> Residente:
    return Residente(
        id=modelo.id,
        nombre=modelo.nombre,
        documento=modelo.documento,
        tipo_residente=TipoResidente(
            id=modelo.tipo_residente_id,
            codigo=modelo.tipo_residente_rel.codigo,
            nombre=modelo.tipo_residente_rel.nombre,
        ),
        apartamento_id=modelo.apartamento_id,
        unidad_negocio_id=modelo.unidad_negocio_id,
        telefono_1=modelo.telefono_1,
        telefono_2=modelo.telefono_2,
        activo=modelo.activo,
        created_at=modelo.created_at,
        updated_at=modelo.updated_at,
        vehiculos=[_vehiculo_a_entidad(v) for v in modelo.vehiculos],
    )


class ResidenteRepository(IResidenteRepository):
    def __init__(self, sesion: AsyncSession) -> None:
        self._sesion = sesion

    async def obtener_por_id(self, residente_id: int) -> Residente | None:
        consulta = (
            select(ResidenteModel)
            .where(ResidenteModel.id == residente_id)
            .options(selectinload(ResidenteModel.vehiculos))
        )
        resultado = await self._sesion.execute(consulta)
        modelo = resultado.scalar_one_or_none()
        return _a_entidad(modelo) if modelo else None

    async def listar(
        self,
        unidad_negocio_id: int,
        skip: int = 0,
        limit: int = 50,
        busqueda: str | None = None,
    ) -> list[Residente]:
        consulta = (
            select(ResidenteModel)
            .where(ResidenteModel.unidad_negocio_id == unidad_negocio_id)
            .options(selectinload(ResidenteModel.vehiculos))
        )
        if busqueda:
            patron = f"%{busqueda}%"
            consulta = consulta.where(
                or_(ResidenteModel.nombre.ilike(patron), ResidenteModel.documento.ilike(patron))
            )
        consulta = consulta.offset(skip).limit(limit).order_by(ResidenteModel.nombre)
        resultado = await self._sesion.execute(consulta)
        return [_a_entidad(m) for m in resultado.scalars().all()]

    async def crear(self, residente: Residente) -> Residente:
        modelo = ResidenteModel(
            nombre=residente.nombre,
            documento=residente.documento,
            tipo_residente_id=residente.tipo_residente.id,
            apartamento_id=residente.apartamento_id,
            unidad_negocio_id=residente.unidad_negocio_id,
            telefono_1=residente.telefono_1,
            telefono_2=residente.telefono_2,
            activo=residente.activo,
        )
        self._sesion.add(modelo)
        await self._sesion.commit()
        await self._sesion.refresh(modelo)
        await self._sesion.refresh(modelo, attribute_names=["vehiculos", "tipo_residente_rel"])
        return _a_entidad(modelo)

    async def actualizar(self, residente: Residente) -> Residente:
        consulta = (
            select(ResidenteModel)
            .where(ResidenteModel.id == residente.id)
            .options(selectinload(ResidenteModel.vehiculos))
        )
        resultado = await self._sesion.execute(consulta)
        modelo = resultado.scalar_one_or_none()
        if modelo is None:
            raise ValueError("Residente no encontrado para actualizar")

        modelo.nombre = residente.nombre
        modelo.documento = residente.documento
        modelo.tipo_residente_id = residente.tipo_residente.id
        modelo.apartamento_id = residente.apartamento_id
        modelo.telefono_1 = residente.telefono_1
        modelo.telefono_2 = residente.telefono_2
        modelo.activo = residente.activo

        await self._sesion.commit()
        await self._sesion.refresh(modelo)
        await self._sesion.refresh(modelo, attribute_names=["vehiculos", "tipo_residente_rel"])
        return _a_entidad(modelo)

    async def eliminar(self, residente_id: int) -> None:
        modelo = await self._sesion.get(ResidenteModel, residente_id)
        if modelo is not None:
            await self._sesion.delete(modelo)
            await self._sesion.commit()

    async def existe_documento(
        self, unidad_negocio_id: int, documento: str, excluir_id: int | None = None
    ) -> bool:
        consulta = select(ResidenteModel.id).where(
            ResidenteModel.unidad_negocio_id == unidad_negocio_id,
            ResidenteModel.documento == documento,
        )
        if excluir_id is not None:
            consulta = consulta.where(ResidenteModel.id != excluir_id)
        resultado = await self._sesion.execute(consulta)
        return resultado.first() is not None
