"""Casos de uso para la gestión de residentes, aislados por unidad de negocio."""
from app.application.dto.residente_dto import ActualizarResidenteDTO, CrearResidenteDTO
from app.domain.entities.residente import Residente
from app.domain.exceptions.excepciones import DocumentoDuplicadoError, EntidadNoEncontradaError
from app.domain.repositories.apartamento_repository import IApartamentoRepository
from app.domain.repositories.residente_repository import IResidenteRepository
from app.domain.repositories.tipo_residente_repository import ITipoResidenteRepository
from app.domain.repositories.vehiculo_repository import IVehiculoRepository
from app.domain.services.validador_reglas_vehiculo import ValidadorReglasVehiculo


class CrearResidenteUseCase:
    def __init__(
        self,
        residente_repository: IResidenteRepository,
        apartamento_repository: IApartamentoRepository,
        tipo_residente_repository: ITipoResidenteRepository,
    ) -> None:
        self._residentes = residente_repository
        self._apartamentos = apartamento_repository
        self._tipos_residente = tipo_residente_repository

    async def ejecutar(self, unidad_negocio_id: int, datos: CrearResidenteDTO) -> Residente:
        if await self._residentes.existe_documento(unidad_negocio_id, datos.documento):
            raise DocumentoDuplicadoError(
                f"El documento {datos.documento} ya está registrado"
            )

        apartamento = await self._apartamentos.obtener_por_id(datos.apartamento_id)
        if apartamento is None or apartamento.unidad_negocio_id != unidad_negocio_id:
            raise EntidadNoEncontradaError("El apartamento indicado no existe")

        tipo_residente = await self._tipos_residente.obtener_por_id(datos.tipo_residente_id)
        if tipo_residente is None:
            raise EntidadNoEncontradaError("El tipo de residente indicado no existe")

        residente = Residente(
            id=None,
            nombre=datos.nombre,
            documento=datos.documento,
            tipo_residente=tipo_residente,
            apartamento_id=datos.apartamento_id,
            unidad_negocio_id=unidad_negocio_id,
            telefono_1=datos.telefono_1,
            telefono_2=datos.telefono_2,
        )
        return await self._residentes.crear(residente)


class ListarResidentesUseCase:
    def __init__(self, residente_repository: IResidenteRepository) -> None:
        self._residentes = residente_repository

    async def ejecutar(
        self, unidad_negocio_id: int, skip: int = 0, limit: int = 50, busqueda: str | None = None
    ) -> list[Residente]:
        return await self._residentes.listar(unidad_negocio_id, skip=skip, limit=limit, busqueda=busqueda)


async def _obtener_residente_del_tenant(
    residentes: IResidenteRepository, unidad_negocio_id: int, residente_id: int
) -> Residente:
    residente = await residentes.obtener_por_id(residente_id)
    if residente is None or residente.unidad_negocio_id != unidad_negocio_id:
        raise EntidadNoEncontradaError("El residente no existe")
    return residente


class ObtenerResidenteUseCase:
    def __init__(self, residente_repository: IResidenteRepository) -> None:
        self._residentes = residente_repository

    async def ejecutar(self, unidad_negocio_id: int, residente_id: int) -> Residente:
        return await _obtener_residente_del_tenant(self._residentes, unidad_negocio_id, residente_id)


class ActualizarResidenteUseCase:
    """Actualiza un residente. Si cambia el tipo, revalida sus vehículos actuales."""

    def __init__(
        self,
        residente_repository: IResidenteRepository,
        apartamento_repository: IApartamentoRepository,
        vehiculo_repository: IVehiculoRepository,
        tipo_residente_repository: ITipoResidenteRepository,
        validador: ValidadorReglasVehiculo,
    ) -> None:
        self._residentes = residente_repository
        self._apartamentos = apartamento_repository
        self._vehiculos = vehiculo_repository
        self._tipos_residente = tipo_residente_repository
        self._validador = validador

    async def ejecutar(
        self, unidad_negocio_id: int, residente_id: int, datos: ActualizarResidenteDTO
    ) -> Residente:
        residente_actual = await _obtener_residente_del_tenant(
            self._residentes, unidad_negocio_id, residente_id
        )

        if datos.documento != residente_actual.documento and await self._residentes.existe_documento(
            unidad_negocio_id, datos.documento, excluir_id=residente_id
        ):
            raise DocumentoDuplicadoError(f"El documento {datos.documento} ya está registrado")

        apartamento = await self._apartamentos.obtener_por_id(datos.apartamento_id)
        if apartamento is None or apartamento.unidad_negocio_id != unidad_negocio_id:
            raise EntidadNoEncontradaError("El apartamento indicado no existe")

        tipo_residente = await self._tipos_residente.obtener_por_id(datos.tipo_residente_id)
        if tipo_residente is None:
            raise EntidadNoEncontradaError("El tipo de residente indicado no existe")

        if tipo_residente.id != residente_actual.tipo_residente.id:
            vehiculos_actuales = await self._vehiculos.listar_por_residente(residente_id)
            self._validador.validar_cambio_tipo_residente(
                nuevo_tipo_residente=tipo_residente,
                vehiculos_actuales=vehiculos_actuales,
            )

        residente_actualizado = Residente(
            id=residente_id,
            nombre=datos.nombre,
            documento=datos.documento,
            tipo_residente=tipo_residente,
            apartamento_id=datos.apartamento_id,
            unidad_negocio_id=unidad_negocio_id,
            telefono_1=datos.telefono_1,
            telefono_2=datos.telefono_2,
            activo=datos.activo,
        )
        return await self._residentes.actualizar(residente_actualizado)


class EliminarResidenteUseCase:
    def __init__(self, residente_repository: IResidenteRepository) -> None:
        self._residentes = residente_repository

    async def ejecutar(self, unidad_negocio_id: int, residente_id: int) -> None:
        await _obtener_residente_del_tenant(self._residentes, unidad_negocio_id, residente_id)
        await self._residentes.eliminar(residente_id)
