"""Casos de uso para la gestión de bloques y parqueaderos, aislados por unidad de negocio."""
from app.application.dto.parqueadero_dto import (
    ActualizarBloqueDTO,
    ActualizarParqueaderoDTO,
    CrearBloqueDTO,
    CrearParqueaderoDTO,
    ParqueaderoConOcupacionDTO,
)
from app.domain.entities.bloque import Bloque
from app.domain.entities.parqueadero import COMUNAL, Parqueadero
from app.domain.exceptions.excepciones import (
    CodigoBloqueDuplicadoError,
    EntidadNoEncontradaError,
    ParqueaderoDuplicadoError,
    PropietarioInvalidoError,
)
from app.domain.repositories.bloque_repository import IBloqueRepository
from app.domain.repositories.parqueadero_repository import IParqueaderoRepository
from app.domain.repositories.residente_repository import IResidenteRepository
from app.domain.repositories.tipo_vehiculo_repository import ITipoVehiculoRepository
from app.domain.repositories.vehiculo_repository import IVehiculoRepository


async def _obtener_bloque_del_tenant(
    bloques: IBloqueRepository, unidad_negocio_id: int, bloque_id: int
) -> Bloque:
    bloque = await bloques.obtener_por_id(bloque_id)
    if bloque is None or bloque.unidad_negocio_id != unidad_negocio_id:
        raise EntidadNoEncontradaError("El bloque no existe")
    return bloque


class CrearBloqueUseCase:
    def __init__(self, bloque_repository: IBloqueRepository) -> None:
        self._bloques = bloque_repository

    async def ejecutar(self, unidad_negocio_id: int, datos: CrearBloqueDTO) -> Bloque:
        if await self._bloques.existe_codigo(unidad_negocio_id, datos.codigo):
            raise CodigoBloqueDuplicadoError(f"El código de bloque {datos.codigo} ya existe")
        return await self._bloques.crear(
            Bloque(id=None, nombre=datos.nombre, codigo=datos.codigo, unidad_negocio_id=unidad_negocio_id)
        )


class ListarBloquesUseCase:
    def __init__(self, bloque_repository: IBloqueRepository) -> None:
        self._bloques = bloque_repository

    async def ejecutar(self, unidad_negocio_id: int) -> list[Bloque]:
        return await self._bloques.listar(unidad_negocio_id)


class ActualizarBloqueUseCase:
    def __init__(self, bloque_repository: IBloqueRepository) -> None:
        self._bloques = bloque_repository

    async def ejecutar(self, unidad_negocio_id: int, bloque_id: int, datos: ActualizarBloqueDTO) -> Bloque:
        await _obtener_bloque_del_tenant(self._bloques, unidad_negocio_id, bloque_id)
        if await self._bloques.existe_codigo(unidad_negocio_id, datos.codigo, excluir_id=bloque_id):
            raise CodigoBloqueDuplicadoError(f"El código de bloque {datos.codigo} ya existe")
        return await self._bloques.actualizar(
            Bloque(id=bloque_id, nombre=datos.nombre, codigo=datos.codigo, unidad_negocio_id=unidad_negocio_id)
        )


class EliminarBloqueUseCase:
    def __init__(self, bloque_repository: IBloqueRepository) -> None:
        self._bloques = bloque_repository

    async def ejecutar(self, unidad_negocio_id: int, bloque_id: int) -> None:
        await _obtener_bloque_del_tenant(self._bloques, unidad_negocio_id, bloque_id)
        await self._bloques.eliminar(bloque_id)


async def _obtener_parqueadero_del_tenant(
    parqueaderos: IParqueaderoRepository, unidad_negocio_id: int, parqueadero_id: int
) -> Parqueadero:
    parqueadero = await parqueaderos.obtener_por_id(parqueadero_id)
    if parqueadero is None or parqueadero.unidad_negocio_id != unidad_negocio_id:
        raise EntidadNoEncontradaError("El parqueadero no existe")
    return parqueadero


async def _resolver_propietario(
    residentes: IResidenteRepository,
    unidad_negocio_id: int,
    tipo_espacio: str,
    propietario_residente_id: int | None,
) -> int | None:
    if tipo_espacio == COMUNAL:
        return None

    if propietario_residente_id is None:
        raise PropietarioInvalidoError(
            "Un parqueadero privado debe tener un residente propietario asignado"
        )
    residente = await residentes.obtener_por_id(propietario_residente_id)
    if residente is None or residente.unidad_negocio_id != unidad_negocio_id:
        raise EntidadNoEncontradaError("El residente propietario indicado no existe")
    if residente.tipo_residente.codigo != "PROPIETARIO":
        raise PropietarioInvalidoError(
            "El dueño de un parqueadero privado debe ser un residente propietario"
        )
    return propietario_residente_id


class CrearParqueaderoUseCase:
    def __init__(
        self,
        parqueadero_repository: IParqueaderoRepository,
        bloque_repository: IBloqueRepository,
        residente_repository: IResidenteRepository,
        tipo_vehiculo_repository: ITipoVehiculoRepository,
    ) -> None:
        self._parqueaderos = parqueadero_repository
        self._bloques = bloque_repository
        self._residentes = residente_repository
        self._tipos_vehiculo = tipo_vehiculo_repository

    async def ejecutar(self, unidad_negocio_id: int, datos: CrearParqueaderoDTO) -> ParqueaderoConOcupacionDTO:
        await _obtener_bloque_del_tenant(self._bloques, unidad_negocio_id, datos.bloque_id)

        if await self._parqueaderos.existe_numero_en_bloque(datos.bloque_id, datos.numero):
            raise ParqueaderoDuplicadoError(f"El parqueadero {datos.numero} ya existe en este bloque")

        tipo_vehiculo = await self._tipos_vehiculo.obtener_por_id(datos.tipo_vehiculo_id)
        if tipo_vehiculo is None:
            raise EntidadNoEncontradaError("El tipo de vehículo indicado no existe")

        if datos.capacidad < 1:
            raise EntidadNoEncontradaError("La capacidad debe ser al menos 1")

        propietario_residente_id = await _resolver_propietario(
            self._residentes, unidad_negocio_id, datos.tipo_espacio, datos.propietario_residente_id
        )

        nuevo = Parqueadero(
            id=None,
            bloque_id=datos.bloque_id,
            numero=datos.numero,
            tipo_espacio=datos.tipo_espacio,
            tipo_vehiculo=tipo_vehiculo,
            capacidad=datos.capacidad,
            unidad_negocio_id=unidad_negocio_id,
            propietario_residente_id=propietario_residente_id,
        )
        creado = await self._parqueaderos.crear(nuevo)
        return ParqueaderoConOcupacionDTO(parqueadero=creado, vehiculos_asignados=0)


class ListarParqueaderosUseCase:
    def __init__(
        self, parqueadero_repository: IParqueaderoRepository, vehiculo_repository: IVehiculoRepository
    ) -> None:
        self._parqueaderos = parqueadero_repository
        self._vehiculos = vehiculo_repository

    async def ejecutar(
        self, unidad_negocio_id: int, bloque_id: int | None = None
    ) -> list[ParqueaderoConOcupacionDTO]:
        parqueaderos = await self._parqueaderos.listar(unidad_negocio_id, bloque_id=bloque_id)
        return [
            ParqueaderoConOcupacionDTO(
                parqueadero=p, vehiculos_asignados=await self._vehiculos.contar_por_parqueadero(p.id)
            )
            for p in parqueaderos
        ]


class ActualizarParqueaderoUseCase:
    def __init__(
        self,
        parqueadero_repository: IParqueaderoRepository,
        bloque_repository: IBloqueRepository,
        residente_repository: IResidenteRepository,
        tipo_vehiculo_repository: ITipoVehiculoRepository,
        vehiculo_repository: IVehiculoRepository,
    ) -> None:
        self._parqueaderos = parqueadero_repository
        self._bloques = bloque_repository
        self._residentes = residente_repository
        self._tipos_vehiculo = tipo_vehiculo_repository
        self._vehiculos = vehiculo_repository

    async def ejecutar(
        self, unidad_negocio_id: int, parqueadero_id: int, datos: ActualizarParqueaderoDTO
    ) -> ParqueaderoConOcupacionDTO:
        await _obtener_parqueadero_del_tenant(self._parqueaderos, unidad_negocio_id, parqueadero_id)
        await _obtener_bloque_del_tenant(self._bloques, unidad_negocio_id, datos.bloque_id)

        if await self._parqueaderos.existe_numero_en_bloque(
            datos.bloque_id, datos.numero, excluir_id=parqueadero_id
        ):
            raise ParqueaderoDuplicadoError(f"El parqueadero {datos.numero} ya existe en este bloque")

        tipo_vehiculo = await self._tipos_vehiculo.obtener_por_id(datos.tipo_vehiculo_id)
        if tipo_vehiculo is None:
            raise EntidadNoEncontradaError("El tipo de vehículo indicado no existe")

        if datos.capacidad < 1:
            raise EntidadNoEncontradaError("La capacidad debe ser al menos 1")

        propietario_residente_id = await _resolver_propietario(
            self._residentes, unidad_negocio_id, datos.tipo_espacio, datos.propietario_residente_id
        )

        actualizado = Parqueadero(
            id=parqueadero_id,
            bloque_id=datos.bloque_id,
            numero=datos.numero,
            tipo_espacio=datos.tipo_espacio,
            tipo_vehiculo=tipo_vehiculo,
            capacidad=datos.capacidad,
            unidad_negocio_id=unidad_negocio_id,
            propietario_residente_id=propietario_residente_id,
            activo=datos.activo,
        )
        guardado = await self._parqueaderos.actualizar(actualizado)
        ocupacion = await self._vehiculos.contar_por_parqueadero(parqueadero_id)
        return ParqueaderoConOcupacionDTO(parqueadero=guardado, vehiculos_asignados=ocupacion)


class EliminarParqueaderoUseCase:
    def __init__(self, parqueadero_repository: IParqueaderoRepository) -> None:
        self._parqueaderos = parqueadero_repository

    async def ejecutar(self, unidad_negocio_id: int, parqueadero_id: int) -> None:
        await _obtener_parqueadero_del_tenant(self._parqueaderos, unidad_negocio_id, parqueadero_id)
        await self._parqueaderos.eliminar(parqueadero_id)