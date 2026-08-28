from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.tipo_vehiculo import TipoVehiculo
from app.domain.entities.vehiculo import Vehiculo
from app.domain.repositories.vehiculo_repository import IVehiculoRepository
from app.domain.value_objects.placa import Placa
from app.infrastructure.database.models import VehiculoModel


def _a_entidad(modelo: VehiculoModel) -> Vehiculo:
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


class VehiculoRepository(IVehiculoRepository):
    def __init__(self, sesion: AsyncSession) -> None:
        self._sesion = sesion

    async def obtener_por_id(self, vehiculo_id: int) -> Vehiculo | None:
        modelo = await self._sesion.get(VehiculoModel, vehiculo_id)
        return _a_entidad(modelo) if modelo else None

    async def obtener_por_placa(self, unidad_negocio_id: int, placa: str) -> Vehiculo | None:
        placa_normalizada = str(Placa(placa))
        resultado = await self._sesion.execute(
            select(VehiculoModel).where(
                VehiculoModel.unidad_negocio_id == unidad_negocio_id,
                VehiculoModel.placa == placa_normalizada,
            )
        )
        modelo = resultado.scalar_one_or_none()
        return _a_entidad(modelo) if modelo else None

    async def listar_por_residente(self, residente_id: int) -> list[Vehiculo]:
        resultado = await self._sesion.execute(
            select(VehiculoModel).where(VehiculoModel.residente_id == residente_id)
        )
        return [_a_entidad(m) for m in resultado.scalars().all()]

    async def listar(
        self,
        unidad_negocio_id: int,
        skip: int = 0,
        limit: int = 50,
        busqueda: str | None = None,
        parqueadero_id: int | None = None,
    ) -> list[Vehiculo]:
        consulta = select(VehiculoModel).where(VehiculoModel.unidad_negocio_id == unidad_negocio_id)
        if busqueda:
            consulta = consulta.where(VehiculoModel.placa.ilike(f"%{busqueda.upper()}%"))
        if parqueadero_id is not None:
            consulta = consulta.where(VehiculoModel.parqueadero_id == parqueadero_id)
        consulta = consulta.offset(skip).limit(limit).order_by(VehiculoModel.placa)
        resultado = await self._sesion.execute(consulta)
        return [_a_entidad(m) for m in resultado.scalars().all()]

    async def crear(self, vehiculo: Vehiculo) -> Vehiculo:
        modelo = VehiculoModel(
            placa=str(vehiculo.placa),
            tipo_vehiculo_id=vehiculo.tipo_vehiculo.id,
            residente_id=vehiculo.residente_id,
            parqueadero_id=vehiculo.parqueadero_id,
            unidad_negocio_id=vehiculo.unidad_negocio_id,
            activo=vehiculo.activo,
        )
        self._sesion.add(modelo)
        await self._sesion.commit()
        await self._sesion.refresh(modelo)
        await self._sesion.refresh(modelo, attribute_names=["tipo_vehiculo_rel"])
        return _a_entidad(modelo)

    async def actualizar(self, vehiculo: Vehiculo) -> Vehiculo:
        modelo = await self._sesion.get(VehiculoModel, vehiculo.id)
        if modelo is None:
            raise ValueError("Vehículo no encontrado para actualizar")
        modelo.placa = str(vehiculo.placa)
        modelo.tipo_vehiculo_id = vehiculo.tipo_vehiculo.id
        modelo.residente_id = vehiculo.residente_id
        modelo.parqueadero_id = vehiculo.parqueadero_id
        modelo.activo = vehiculo.activo
        await self._sesion.commit()
        await self._sesion.refresh(modelo)
        await self._sesion.refresh(modelo, attribute_names=["tipo_vehiculo_rel"])
        return _a_entidad(modelo)

    async def eliminar(self, vehiculo_id: int) -> None:
        modelo = await self._sesion.get(VehiculoModel, vehiculo_id)
        if modelo is not None:
            await self._sesion.delete(modelo)
            await self._sesion.commit()

    async def existe_placa(
        self, unidad_negocio_id: int, placa: str, excluir_id: int | None = None
    ) -> bool:
        placa_normalizada = str(Placa(placa))
        consulta = select(VehiculoModel.id).where(
            VehiculoModel.unidad_negocio_id == unidad_negocio_id,
            VehiculoModel.placa == placa_normalizada,
        )
        if excluir_id is not None:
            consulta = consulta.where(VehiculoModel.id != excluir_id)
        resultado = await self._sesion.execute(consulta)
        return resultado.first() is not None

    async def contar_por_parqueadero(self, parqueadero_id: int, excluir_id: int | None = None) -> int:
        consulta = select(VehiculoModel.id).where(VehiculoModel.parqueadero_id == parqueadero_id)
        if excluir_id is not None:
            consulta = consulta.where(VehiculoModel.id != excluir_id)
        resultado = await self._sesion.execute(consulta)
        return len(resultado.all())
