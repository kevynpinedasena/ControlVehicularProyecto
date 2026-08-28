from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.parqueadero import Parqueadero
from app.domain.entities.tipo_vehiculo import TipoVehiculo
from app.domain.repositories.parqueadero_repository import IParqueaderoRepository
from app.infrastructure.database.models import ParqueaderoModel


def _a_entidad(modelo: ParqueaderoModel) -> Parqueadero:
    return Parqueadero(
        id=modelo.id,
        bloque_id=modelo.bloque_id,
        numero=modelo.numero,
        tipo_espacio=modelo.tipo_espacio,
        tipo_vehiculo=TipoVehiculo(
            id=modelo.tipo_vehiculo_id,
            codigo=modelo.tipo_vehiculo_rel.codigo,
            nombre=modelo.tipo_vehiculo_rel.nombre,
        ),
        capacidad=modelo.capacidad,
        unidad_negocio_id=modelo.unidad_negocio_id,
        propietario_residente_id=modelo.propietario_residente_id,
        activo=modelo.activo,
    )


class ParqueaderoRepository(IParqueaderoRepository):
    def __init__(self, sesion: AsyncSession) -> None:
        self._sesion = sesion

    async def obtener_por_id(self, parqueadero_id: int) -> Parqueadero | None:
        modelo = await self._sesion.get(ParqueaderoModel, parqueadero_id)
        return _a_entidad(modelo) if modelo else None

    async def listar(self, unidad_negocio_id: int, bloque_id: int | None = None) -> list[Parqueadero]:
        consulta = select(ParqueaderoModel).where(
            ParqueaderoModel.unidad_negocio_id == unidad_negocio_id
        )
        if bloque_id is not None:
            consulta = consulta.where(ParqueaderoModel.bloque_id == bloque_id)
        consulta = consulta.order_by(ParqueaderoModel.numero)
        resultado = await self._sesion.execute(consulta)
        return [_a_entidad(m) for m in resultado.scalars().all()]

    async def crear(self, parqueadero: Parqueadero) -> Parqueadero:
        modelo = ParqueaderoModel(
            bloque_id=parqueadero.bloque_id,
            numero=parqueadero.numero,
            tipo_espacio=parqueadero.tipo_espacio,
            tipo_vehiculo_id=parqueadero.tipo_vehiculo.id,
            capacidad=parqueadero.capacidad,
            propietario_residente_id=parqueadero.propietario_residente_id,
            unidad_negocio_id=parqueadero.unidad_negocio_id,
            activo=parqueadero.activo,
        )
        self._sesion.add(modelo)
        await self._sesion.commit()
        await self._sesion.refresh(modelo)
        await self._sesion.refresh(modelo, attribute_names=["tipo_vehiculo_rel"])
        return _a_entidad(modelo)

    async def actualizar(self, parqueadero: Parqueadero) -> Parqueadero:
        modelo = await self._sesion.get(ParqueaderoModel, parqueadero.id)
        if modelo is None:
            raise ValueError("Parqueadero no encontrado para actualizar")
        modelo.bloque_id = parqueadero.bloque_id
        modelo.numero = parqueadero.numero
        modelo.tipo_espacio = parqueadero.tipo_espacio
        modelo.tipo_vehiculo_id = parqueadero.tipo_vehiculo.id
        modelo.capacidad = parqueadero.capacidad
        modelo.propietario_residente_id = parqueadero.propietario_residente_id
        modelo.activo = parqueadero.activo
        await self._sesion.commit()
        await self._sesion.refresh(modelo)
        await self._sesion.refresh(modelo, attribute_names=["tipo_vehiculo_rel"])
        return _a_entidad(modelo)

    async def eliminar(self, parqueadero_id: int) -> None:
        modelo = await self._sesion.get(ParqueaderoModel, parqueadero_id)
        if modelo is not None:
            await self._sesion.delete(modelo)
            await self._sesion.commit()

    async def existe_numero_en_bloque(
        self, bloque_id: int, numero: str, excluir_id: int | None = None
    ) -> bool:
        consulta = select(ParqueaderoModel.id).where(
            ParqueaderoModel.bloque_id == bloque_id, ParqueaderoModel.numero == numero
        )
        if excluir_id is not None:
            consulta = consulta.where(ParqueaderoModel.id != excluir_id)
        resultado = await self._sesion.execute(consulta)
        return resultado.first() is not None