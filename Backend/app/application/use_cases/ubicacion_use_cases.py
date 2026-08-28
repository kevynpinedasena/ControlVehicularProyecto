"""Casos de uso para la gestión de torres y apartamentos, aislados por unidad de negocio."""
from app.application.dto.ubicacion_dto import (
    ActualizarApartamentoDTO,
    ActualizarTorreDTO,
    CrearApartamentoDTO,
    CrearTorreDTO,
)
from app.domain.entities.apartamento import Apartamento
from app.domain.entities.torre import Torre
from app.domain.exceptions.excepciones import (
    ApartamentoDuplicadoError,
    CodigoTorreDuplicadoError,
    EntidadNoEncontradaError,
)
from app.domain.repositories.apartamento_repository import IApartamentoRepository
from app.domain.repositories.torre_repository import ITorreRepository


class CrearTorreUseCase:
    def __init__(self, torre_repository: ITorreRepository) -> None:
        self._torres = torre_repository

    async def ejecutar(self, unidad_negocio_id: int, datos: CrearTorreDTO) -> Torre:
        if await self._torres.existe_codigo(unidad_negocio_id, datos.codigo):
            raise CodigoTorreDuplicadoError(f"El código de torre {datos.codigo} ya existe")
        return await self._torres.crear(
            Torre(id=None, nombre=datos.nombre, codigo=datos.codigo, unidad_negocio_id=unidad_negocio_id)
        )


class ListarTorresUseCase:
    def __init__(self, torre_repository: ITorreRepository) -> None:
        self._torres = torre_repository

    async def ejecutar(self, unidad_negocio_id: int) -> list[Torre]:
        return await self._torres.listar(unidad_negocio_id)


async def _obtener_torre_del_tenant(
    torres: ITorreRepository, unidad_negocio_id: int, torre_id: int
) -> Torre:
    torre = await torres.obtener_por_id(torre_id)
    if torre is None or torre.unidad_negocio_id != unidad_negocio_id:
        raise EntidadNoEncontradaError("La torre no existe")
    return torre


class ActualizarTorreUseCase:
    def __init__(self, torre_repository: ITorreRepository) -> None:
        self._torres = torre_repository

    async def ejecutar(self, unidad_negocio_id: int, torre_id: int, datos: ActualizarTorreDTO) -> Torre:
        await _obtener_torre_del_tenant(self._torres, unidad_negocio_id, torre_id)
        if await self._torres.existe_codigo(unidad_negocio_id, datos.codigo, excluir_id=torre_id):
            raise CodigoTorreDuplicadoError(f"El código de torre {datos.codigo} ya existe")
        return await self._torres.actualizar(
            Torre(id=torre_id, nombre=datos.nombre, codigo=datos.codigo, unidad_negocio_id=unidad_negocio_id)
        )


class EliminarTorreUseCase:
    def __init__(self, torre_repository: ITorreRepository) -> None:
        self._torres = torre_repository

    async def ejecutar(self, unidad_negocio_id: int, torre_id: int) -> None:
        await _obtener_torre_del_tenant(self._torres, unidad_negocio_id, torre_id)
        await self._torres.eliminar(torre_id)


class CrearApartamentoUseCase:
    def __init__(
        self,
        apartamento_repository: IApartamentoRepository,
        torre_repository: ITorreRepository,
    ) -> None:
        self._apartamentos = apartamento_repository
        self._torres = torre_repository

    async def ejecutar(self, unidad_negocio_id: int, datos: CrearApartamentoDTO) -> Apartamento:
        await _obtener_torre_del_tenant(self._torres, unidad_negocio_id, datos.torre_id)
        if await self._apartamentos.existe_numero_en_torre(datos.torre_id, datos.numero):
            raise ApartamentoDuplicadoError(
                f"El apartamento {datos.numero} ya existe en esta torre"
            )
        return await self._apartamentos.crear(
            Apartamento(
                id=None,
                torre_id=datos.torre_id,
                numero=datos.numero,
                unidad_negocio_id=unidad_negocio_id,
            )
        )


class ListarApartamentosUseCase:
    def __init__(self, apartamento_repository: IApartamentoRepository) -> None:
        self._apartamentos = apartamento_repository

    async def ejecutar(self, unidad_negocio_id: int, torre_id: int | None = None) -> list[Apartamento]:
        return await self._apartamentos.listar(unidad_negocio_id, torre_id=torre_id)


async def _obtener_apartamento_del_tenant(
    apartamentos: IApartamentoRepository, unidad_negocio_id: int, apartamento_id: int
) -> Apartamento:
    apartamento = await apartamentos.obtener_por_id(apartamento_id)
    if apartamento is None or apartamento.unidad_negocio_id != unidad_negocio_id:
        raise EntidadNoEncontradaError("El apartamento no existe")
    return apartamento


class ActualizarApartamentoUseCase:
    def __init__(
        self,
        apartamento_repository: IApartamentoRepository,
        torre_repository: ITorreRepository,
    ) -> None:
        self._apartamentos = apartamento_repository
        self._torres = torre_repository

    async def ejecutar(
        self, unidad_negocio_id: int, apartamento_id: int, datos: ActualizarApartamentoDTO
    ) -> Apartamento:
        await _obtener_apartamento_del_tenant(self._apartamentos, unidad_negocio_id, apartamento_id)
        await _obtener_torre_del_tenant(self._torres, unidad_negocio_id, datos.torre_id)
        if await self._apartamentos.existe_numero_en_torre(
            datos.torre_id, datos.numero, excluir_id=apartamento_id
        ):
            raise ApartamentoDuplicadoError(
                f"El apartamento {datos.numero} ya existe en esta torre"
            )
        return await self._apartamentos.actualizar(
            Apartamento(
                id=apartamento_id,
                torre_id=datos.torre_id,
                numero=datos.numero,
                unidad_negocio_id=unidad_negocio_id,
                activo=datos.activo,
            )
        )


class EliminarApartamentoUseCase:
    def __init__(self, apartamento_repository: IApartamentoRepository) -> None:
        self._apartamentos = apartamento_repository

    async def ejecutar(self, unidad_negocio_id: int, apartamento_id: int) -> None:
        await _obtener_apartamento_del_tenant(self._apartamentos, unidad_negocio_id, apartamento_id)
        await self._apartamentos.eliminar(apartamento_id)
