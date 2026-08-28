"""Casos de uso relacionados con el registro y consulta de vehículos, por unidad de negocio."""
from app.application.dto.vehiculo_dto import (
    ActualizarVehiculoDTO,
    AsignarParqueaderoVehiculoDTO,
    CrearVehiculoDTO,
    ResultadoConsultaPlacaDTO,
)
from app.domain.entities.vehiculo import Vehiculo
from app.domain.exceptions.excepciones import (
    EntidadNoEncontradaError,
    ParqueaderoLlenoError,
    PlacaDuplicadaError,
    TipoVehiculoIncompatibleError,
)
from app.domain.repositories.apartamento_repository import IApartamentoRepository
from app.domain.repositories.bloque_repository import IBloqueRepository
from app.domain.repositories.parqueadero_repository import IParqueaderoRepository
from app.domain.repositories.residente_repository import IResidenteRepository
from app.domain.repositories.tipo_vehiculo_repository import ITipoVehiculoRepository
from app.domain.repositories.torre_repository import ITorreRepository
from app.domain.repositories.vehiculo_repository import IVehiculoRepository
from app.domain.services.validador_reglas_vehiculo import ValidadorReglasVehiculo
from app.domain.value_objects.placa import Placa


async def _obtener_vehiculo_del_tenant(
    vehiculos: IVehiculoRepository, unidad_negocio_id: int, vehiculo_id: int
) -> Vehiculo:
    vehiculo = await vehiculos.obtener_por_id(vehiculo_id)
    if vehiculo is None or vehiculo.unidad_negocio_id != unidad_negocio_id:
        raise EntidadNoEncontradaError("El vehículo no existe")
    return vehiculo


class RegistrarVehiculoUseCase:
    """Registra un vehículo validando placa única (por unidad) y reglas del tipo de residente."""

    def __init__(
        self,
        vehiculo_repository: IVehiculoRepository,
        residente_repository: IResidenteRepository,
        tipo_vehiculo_repository: ITipoVehiculoRepository,
        validador: ValidadorReglasVehiculo,
    ) -> None:
        self._vehiculos = vehiculo_repository
        self._residentes = residente_repository
        self._tipos_vehiculo = tipo_vehiculo_repository
        self._validador = validador

    async def ejecutar(self, unidad_negocio_id: int, datos: CrearVehiculoDTO) -> Vehiculo:
        placa = Placa(datos.placa)

        if await self._vehiculos.existe_placa(unidad_negocio_id, str(placa)):
            raise PlacaDuplicadaError(f"La placa {placa} ya se encuentra registrada")

        residente = await self._residentes.obtener_por_id(datos.residente_id)
        if residente is None or residente.unidad_negocio_id != unidad_negocio_id:
            raise EntidadNoEncontradaError("El residente asociado no existe")

        tipo_vehiculo = await self._tipos_vehiculo.obtener_por_id(datos.tipo_vehiculo_id)
        if tipo_vehiculo is None:
            raise EntidadNoEncontradaError("El tipo de vehículo indicado no existe")

        vehiculos_actuales = await self._vehiculos.listar_por_residente(datos.residente_id)
        self._validador.validar_nuevo_vehiculo(
            tipo_residente=residente.tipo_residente,
            vehiculos_actuales=vehiculos_actuales,
            tipo_vehiculo_nuevo=tipo_vehiculo,
        )

        nuevo_vehiculo = Vehiculo(
            id=None,
            placa=placa,
            tipo_vehiculo=tipo_vehiculo,
            residente_id=datos.residente_id,
            unidad_negocio_id=unidad_negocio_id,
        )
        return await self._vehiculos.crear(nuevo_vehiculo)


class ListarVehiculosUseCase:
    def __init__(self, vehiculo_repository: IVehiculoRepository) -> None:
        self._vehiculos = vehiculo_repository

    async def ejecutar(
        self,
        unidad_negocio_id: int,
        skip: int = 0,
        limit: int = 50,
        busqueda: str | None = None,
        parqueadero_id: int | None = None,
    ) -> list[Vehiculo]:
        return await self._vehiculos.listar(
            unidad_negocio_id, skip=skip, limit=limit, busqueda=busqueda, parqueadero_id=parqueadero_id
        )


class ObtenerVehiculoUseCase:
    def __init__(self, vehiculo_repository: IVehiculoRepository) -> None:
        self._vehiculos = vehiculo_repository

    async def ejecutar(self, unidad_negocio_id: int, vehiculo_id: int) -> Vehiculo:
        return await _obtener_vehiculo_del_tenant(self._vehiculos, unidad_negocio_id, vehiculo_id)


class ActualizarVehiculoUseCase:
    """Actualiza un vehículo revalidando reglas de negocio si cambia el tipo."""

    def __init__(
        self,
        vehiculo_repository: IVehiculoRepository,
        residente_repository: IResidenteRepository,
        tipo_vehiculo_repository: ITipoVehiculoRepository,
        validador: ValidadorReglasVehiculo,
    ) -> None:
        self._vehiculos = vehiculo_repository
        self._residentes = residente_repository
        self._tipos_vehiculo = tipo_vehiculo_repository
        self._validador = validador

    async def ejecutar(
        self, unidad_negocio_id: int, vehiculo_id: int, datos: ActualizarVehiculoDTO
    ) -> Vehiculo:
        vehiculo_actual = await _obtener_vehiculo_del_tenant(
            self._vehiculos, unidad_negocio_id, vehiculo_id
        )

        placa_nueva = Placa(datos.placa)
        if str(placa_nueva) != str(vehiculo_actual.placa) and await self._vehiculos.existe_placa(
            unidad_negocio_id, str(placa_nueva), excluir_id=vehiculo_id
        ):
            raise PlacaDuplicadaError(f"La placa {placa_nueva} ya se encuentra registrada")

        residente = await self._residentes.obtener_por_id(vehiculo_actual.residente_id)
        if residente is None:
            raise EntidadNoEncontradaError("El residente asociado no existe")

        tipo_vehiculo = await self._tipos_vehiculo.obtener_por_id(datos.tipo_vehiculo_id)
        if tipo_vehiculo is None:
            raise EntidadNoEncontradaError("El tipo de vehículo indicado no existe")

        otros_vehiculos = [
            v for v in await self._vehiculos.listar_por_residente(residente.id) if v.id != vehiculo_id
        ]
        self._validador.validar_nuevo_vehiculo(
            tipo_residente=residente.tipo_residente,
            vehiculos_actuales=otros_vehiculos,
            tipo_vehiculo_nuevo=tipo_vehiculo,
        )

        vehiculo_actualizado = Vehiculo(
            id=vehiculo_id,
            placa=placa_nueva,
            tipo_vehiculo=tipo_vehiculo,
            residente_id=vehiculo_actual.residente_id,
            unidad_negocio_id=unidad_negocio_id,
            parqueadero_id=vehiculo_actual.parqueadero_id,
            activo=datos.activo,
        )
        return await self._vehiculos.actualizar(vehiculo_actualizado)


class AsignarParqueaderoVehiculoUseCase:
    """Asigna, reasigna o desasigna (parqueadero_id=None) el parqueadero de un vehículo,
    validando que el tipo de vehículo coincida con el del parqueadero y que haya cupo."""

    def __init__(
        self,
        vehiculo_repository: IVehiculoRepository,
        parqueadero_repository: IParqueaderoRepository,
    ) -> None:
        self._vehiculos = vehiculo_repository
        self._parqueaderos = parqueadero_repository

    async def ejecutar(
        self, unidad_negocio_id: int, vehiculo_id: int, datos: AsignarParqueaderoVehiculoDTO
    ) -> Vehiculo:
        vehiculo = await _obtener_vehiculo_del_tenant(self._vehiculos, unidad_negocio_id, vehiculo_id)

        if datos.parqueadero_id is None:
            vehiculo.parqueadero_id = None
            return await self._vehiculos.actualizar(vehiculo)

        parqueadero = await self._parqueaderos.obtener_por_id(datos.parqueadero_id)
        if parqueadero is None or parqueadero.unidad_negocio_id != unidad_negocio_id:
            raise EntidadNoEncontradaError("El parqueadero indicado no existe")

        if vehiculo.tipo_vehiculo.codigo != parqueadero.tipo_vehiculo.codigo:
            raise TipoVehiculoIncompatibleError(
                f"Este parqueadero solo admite vehículos de tipo {parqueadero.tipo_vehiculo.nombre}"
            )

        ocupados = await self._vehiculos.contar_por_parqueadero(
            parqueadero.id, excluir_id=vehiculo_id
        )
        if ocupados >= parqueadero.capacidad:
            raise ParqueaderoLlenoError(
                f"El parqueadero {parqueadero.numero} ya alcanzó su capacidad de {parqueadero.capacidad}"
            )

        vehiculo.parqueadero_id = parqueadero.id
        return await self._vehiculos.actualizar(vehiculo)


class EliminarVehiculoUseCase:
    def __init__(self, vehiculo_repository: IVehiculoRepository) -> None:
        self._vehiculos = vehiculo_repository

    async def ejecutar(self, unidad_negocio_id: int, vehiculo_id: int) -> None:
        await _obtener_vehiculo_del_tenant(self._vehiculos, unidad_negocio_id, vehiculo_id)
        await self._vehiculos.eliminar(vehiculo_id)


class ConsultarPlacaUseCase:
    """Caso de uso crítico: permite al vigilante saber si una placa está registrada."""

    def __init__(
        self,
        vehiculo_repository: IVehiculoRepository,
        residente_repository: IResidenteRepository,
        apartamento_repository: IApartamentoRepository,
        torre_repository: ITorreRepository,
        parqueadero_repository: IParqueaderoRepository,
        bloque_repository: IBloqueRepository,
    ) -> None:
        self._vehiculos = vehiculo_repository
        self._residentes = residente_repository
        self._apartamentos = apartamento_repository
        self._torres = torre_repository
        self._parqueaderos = parqueadero_repository
        self._bloques = bloque_repository

    async def ejecutar(self, unidad_negocio_id: int, placa: str) -> ResultadoConsultaPlacaDTO:
        placa_normalizada = str(Placa(placa))
        vehiculo = await self._vehiculos.obtener_por_placa(unidad_negocio_id, placa_normalizada)

        if vehiculo is None or not vehiculo.activo:
            return ResultadoConsultaPlacaDTO(
                registrado=False,
                placa=placa_normalizada,
                mensaje=(
                    f"El vehículo con placa {placa_normalizada} no se encuentra "
                    "registrado en el conjunto"
                ),
            )

        residente = await self._residentes.obtener_por_id(vehiculo.residente_id)
        apartamento = await self._apartamentos.obtener_por_id(residente.apartamento_id)
        torre = await self._torres.obtener_por_id(apartamento.torre_id)

        parqueadero_texto = None
        if vehiculo.parqueadero_id is not None:
            parqueadero = await self._parqueaderos.obtener_por_id(vehiculo.parqueadero_id)
            if parqueadero is not None:
                bloque = await self._bloques.obtener_por_id(parqueadero.bloque_id)
                nombre_bloque = bloque.nombre if bloque is not None else "—"
                parqueadero_texto = f"{nombre_bloque} · {parqueadero.numero}"

        return ResultadoConsultaPlacaDTO(
            registrado=True,
            placa=placa_normalizada,
            tipo_vehiculo=vehiculo.tipo_vehiculo,
            torre=torre.nombre,
            apartamento=apartamento.numero,
            tipo_residente=residente.tipo_residente,
            estado="REGISTRADO" if residente.activo else "RESIDENTE_INACTIVO",
            telefono_1=residente.telefono_1,
            telefono_2=residente.telefono_2,
            parqueadero=parqueadero_texto,
        )
