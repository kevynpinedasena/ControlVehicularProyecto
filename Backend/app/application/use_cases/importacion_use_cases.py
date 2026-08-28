"""Caso de uso de carga masiva: reutiliza los casos de uso existentes para que se respeten
las mismas reglas de negocio (placas únicas, máximo de vehículos por residente, etc.) que en
el alta manual, fila por fila, sin detener el proceso ante un error individual.

Cada fila se procesa como "upsert" por su clave natural (código de torre, torre+número de
apartamento, documento de residente, placa de vehículo): si la clave ya existe se actualiza
el registro, y si no existe se crea uno nuevo. Los campos que el Excel no incluye (por ejemplo
el estado activo/inactivo) se conservan tal como estaban. Nota: al actualizar un vehículo por
placa, el residente asociado NO se reasigna (igual que en la edición manual), solo se
actualizan su tipo y su estado.
"""
from app.application.dto.importacion_dto import (
    DatosImportacion,
    DetalleImportacionDTO,
    ErrorImportacionDTO,
    ReporteImportacionDTO,
)
from app.application.dto.parqueadero_dto import (
    ActualizarBloqueDTO,
    ActualizarParqueaderoDTO,
    CrearBloqueDTO,
    CrearParqueaderoDTO,
)
from app.application.dto.residente_dto import ActualizarResidenteDTO, CrearResidenteDTO
from app.application.dto.ubicacion_dto import (
    ActualizarApartamentoDTO,
    ActualizarTorreDTO,
    CrearApartamentoDTO,
    CrearTorreDTO,
)
from app.application.dto.vehiculo_dto import (
    ActualizarVehiculoDTO,
    AsignarParqueaderoVehiculoDTO,
    CrearVehiculoDTO,
)
from app.application.use_cases.parqueadero_use_cases import (
    ActualizarBloqueUseCase,
    ActualizarParqueaderoUseCase,
    CrearBloqueUseCase,
    CrearParqueaderoUseCase,
)
from app.application.use_cases.residente_use_cases import (
    ActualizarResidenteUseCase,
    CrearResidenteUseCase,
)
from app.application.use_cases.ubicacion_use_cases import (
    ActualizarApartamentoUseCase,
    ActualizarTorreUseCase,
    CrearApartamentoUseCase,
    CrearTorreUseCase,
)
from app.application.use_cases.vehiculo_use_cases import (
    ActualizarVehiculoUseCase,
    AsignarParqueaderoVehiculoUseCase,
    RegistrarVehiculoUseCase,
)
from app.domain.entities.apartamento import Apartamento
from app.domain.entities.parqueadero import COMUNAL, PRIVADO, Parqueadero
from app.domain.entities.residente import Residente
from app.domain.exceptions.excepciones import ErrorDominio
from app.domain.repositories.apartamento_repository import IApartamentoRepository
from app.domain.repositories.bloque_repository import IBloqueRepository
from app.domain.repositories.parqueadero_repository import IParqueaderoRepository
from app.domain.repositories.residente_repository import IResidenteRepository
from app.domain.repositories.tipo_residente_repository import ITipoResidenteRepository
from app.domain.repositories.tipo_vehiculo_repository import ITipoVehiculoRepository
from app.domain.repositories.torre_repository import ITorreRepository
from app.domain.repositories.vehiculo_repository import IVehiculoRepository
from app.domain.services.validador_reglas_vehiculo import ValidadorReglasVehiculo
from app.domain.value_objects.placa import Placa


class ImportarDatosMasivosUseCase:
    def __init__(
        self,
        torre_repository: ITorreRepository,
        apartamento_repository: IApartamentoRepository,
        residente_repository: IResidenteRepository,
        vehiculo_repository: IVehiculoRepository,
        tipo_residente_repository: ITipoResidenteRepository,
        tipo_vehiculo_repository: ITipoVehiculoRepository,
        bloque_repository: IBloqueRepository,
        parqueadero_repository: IParqueaderoRepository,
    ) -> None:
        self._torres = torre_repository
        self._apartamentos = apartamento_repository
        self._residentes = residente_repository
        self._vehiculos = vehiculo_repository
        self._tipos_residente = tipo_residente_repository
        self._tipos_vehiculo = tipo_vehiculo_repository
        self._bloques = bloque_repository
        self._parqueaderos = parqueadero_repository

    async def ejecutar(self, unidad_negocio_id: int, datos: DatosImportacion) -> ReporteImportacionDTO:
        reporte = ReporteImportacionDTO()

        mapa_torres = await self._procesar_torres(unidad_negocio_id, datos, reporte)
        mapa_apartamentos = await self._procesar_apartamentos(unidad_negocio_id, datos, mapa_torres, reporte)
        mapa_residentes = await self._procesar_residentes(unidad_negocio_id, datos, mapa_apartamentos, reporte)
        mapa_bloques = await self._procesar_bloques(unidad_negocio_id, datos, reporte)
        mapa_parqueaderos = await self._procesar_parqueaderos(
            unidad_negocio_id, datos, mapa_bloques, mapa_residentes, reporte
        )
        await self._procesar_vehiculos(unidad_negocio_id, datos, mapa_residentes, mapa_parqueaderos, reporte)

        return reporte

    async def _procesar_torres(
        self, unidad_negocio_id: int, datos: DatosImportacion, reporte: ReporteImportacionDTO
    ) -> dict[str, int]:
        mapa: dict[str, int] = {t.codigo: t.id for t in await self._torres.listar(unidad_negocio_id)}
        caso_uso_crear = CrearTorreUseCase(self._torres)
        caso_uso_actualizar = ActualizarTorreUseCase(self._torres)

        for fila in datos.torres:
            nombre, codigo = fila.obtener("nombre"), fila.obtener("codigo")
            if not nombre or not codigo:
                reporte.errores.append(
                    ErrorImportacionDTO("Torres", fila.numero_fila, "nombre y codigo son obligatorios")
                )
                continue
            try:
                if codigo in mapa:
                    torre = await caso_uso_actualizar.ejecutar(
                        unidad_negocio_id, mapa[codigo], ActualizarTorreDTO(nombre=nombre, codigo=codigo)
                    )
                    reporte.torres_actualizadas += 1
                    accion = "actualizado"
                else:
                    torre = await caso_uso_crear.ejecutar(
                        unidad_negocio_id, CrearTorreDTO(nombre=nombre, codigo=codigo)
                    )
                    reporte.torres_creadas += 1
                    accion = "creado"
                mapa[codigo] = torre.id
                reporte.detalles.append(
                    DetalleImportacionDTO("Torres", fila.numero_fila, accion, f"{codigo} · {nombre}")
                )
            except ErrorDominio as error:
                reporte.errores.append(ErrorImportacionDTO("Torres", fila.numero_fila, error.mensaje))

        return mapa

    async def _procesar_apartamentos(
        self,
        unidad_negocio_id: int,
        datos: DatosImportacion,
        mapa_torres: dict[str, int],
        reporte: ReporteImportacionDTO,
    ) -> dict[tuple[int, str], int]:
        apartamentos_existentes: dict[tuple[int, str], Apartamento] = {}
        for torre_id in mapa_torres.values():
            for apartamento in await self._apartamentos.listar(unidad_negocio_id, torre_id=torre_id):
                apartamentos_existentes[(apartamento.torre_id, apartamento.numero)] = apartamento

        mapa: dict[tuple[int, str], int] = {
            clave: a.id for clave, a in apartamentos_existentes.items()
        }
        caso_uso_crear = CrearApartamentoUseCase(self._apartamentos, self._torres)
        caso_uso_actualizar = ActualizarApartamentoUseCase(self._apartamentos, self._torres)

        for fila in datos.apartamentos:
            torre_codigo, numero = fila.obtener("torre_codigo"), fila.obtener("numero")
            if not torre_codigo or not numero:
                reporte.errores.append(
                    ErrorImportacionDTO(
                        "Apartamentos", fila.numero_fila, "torre_codigo y numero son obligatorios"
                    )
                )
                continue
            torre_id = mapa_torres.get(torre_codigo)
            if torre_id is None:
                reporte.errores.append(
                    ErrorImportacionDTO(
                        "Apartamentos", fila.numero_fila, f"La torre '{torre_codigo}' no existe"
                    )
                )
                continue
            clave = (torre_id, numero)
            try:
                if clave in mapa:
                    activo_actual = apartamentos_existentes[clave].activo
                    apartamento = await caso_uso_actualizar.ejecutar(
                        unidad_negocio_id,
                        mapa[clave],
                        ActualizarApartamentoDTO(torre_id=torre_id, numero=numero, activo=activo_actual),
                    )
                    reporte.apartamentos_actualizados += 1
                    accion = "actualizado"
                else:
                    apartamento = await caso_uso_crear.ejecutar(
                        unidad_negocio_id, CrearApartamentoDTO(torre_id=torre_id, numero=numero)
                    )
                    reporte.apartamentos_creados += 1
                    accion = "creado"
                mapa[clave] = apartamento.id
                reporte.detalles.append(
                    DetalleImportacionDTO(
                        "Apartamentos",
                        fila.numero_fila,
                        accion,
                        f"Torre {torre_codigo} · Apto {numero}",
                    )
                )
            except ErrorDominio as error:
                reporte.errores.append(ErrorImportacionDTO("Apartamentos", fila.numero_fila, error.mensaje))

        return mapa

    async def _procesar_residentes(
        self,
        unidad_negocio_id: int,
        datos: DatosImportacion,
        mapa_apartamentos: dict[tuple[int, str], int],
        reporte: ReporteImportacionDTO,
    ) -> dict[str, int]:
        mapa_torres_por_codigo: dict[str, int] = {
            t.codigo: t.id for t in await self._torres.listar(unidad_negocio_id)
        }
        residentes_existentes: dict[str, Residente] = {
            r.documento: r
            for r in await self._residentes.listar(unidad_negocio_id, skip=0, limit=100000)
        }
        mapa: dict[str, int] = {doc: r.id for doc, r in residentes_existentes.items()}
        mapa_tipos_residente = {t.codigo: t for t in await self._tipos_residente.listar()}
        caso_uso_crear = CrearResidenteUseCase(self._residentes, self._apartamentos, self._tipos_residente)
        caso_uso_actualizar = ActualizarResidenteUseCase(
            self._residentes,
            self._apartamentos,
            self._vehiculos,
            self._tipos_residente,
            ValidadorReglasVehiculo(),
        )

        for fila in datos.residentes:
            nombre = fila.obtener("nombre")
            documento = fila.obtener("documento")
            tipo_raw = fila.obtener("tipo_residente").upper()
            torre_codigo = fila.obtener("torre_codigo")
            apartamento_numero = fila.obtener("apartamento_numero")
            telefono_1 = fila.obtener("telefono_1") or None
            telefono_2 = fila.obtener("telefono_2") or None

            if not nombre or not documento or not torre_codigo or not apartamento_numero:
                reporte.errores.append(
                    ErrorImportacionDTO(
                        "Residentes",
                        fila.numero_fila,
                        "nombre, documento, torre_codigo y apartamento_numero son obligatorios",
                    )
                )
                continue
            if tipo_raw not in mapa_tipos_residente:
                reporte.errores.append(
                    ErrorImportacionDTO(
                        "Residentes",
                        fila.numero_fila,
                        f"tipo_residente inválido: '{tipo_raw}' (usa PROPIETARIO o ARRENDATARIO)",
                    )
                )
                continue

            torre_id = mapa_torres_por_codigo.get(torre_codigo)
            apartamento_id = mapa_apartamentos.get((torre_id, apartamento_numero)) if torre_id else None
            if apartamento_id is None:
                reporte.errores.append(
                    ErrorImportacionDTO(
                        "Residentes",
                        fila.numero_fila,
                        f"No existe el apartamento '{apartamento_numero}' en la torre '{torre_codigo}'",
                    )
                )
                continue

            try:
                if documento in mapa:
                    activo_actual = residentes_existentes[documento].activo
                    residente = await caso_uso_actualizar.ejecutar(
                        unidad_negocio_id,
                        mapa[documento],
                        ActualizarResidenteDTO(
                            nombre=nombre,
                            documento=documento,
                            tipo_residente_id=mapa_tipos_residente[tipo_raw].id,
                            apartamento_id=apartamento_id,
                            activo=activo_actual,
                            telefono_1=telefono_1,
                            telefono_2=telefono_2,
                        ),
                    )
                    reporte.residentes_actualizados += 1
                    accion = "actualizado"
                else:
                    residente = await caso_uso_crear.ejecutar(
                        unidad_negocio_id,
                        CrearResidenteDTO(
                            nombre=nombre,
                            documento=documento,
                            tipo_residente_id=mapa_tipos_residente[tipo_raw].id,
                            apartamento_id=apartamento_id,
                            telefono_1=telefono_1,
                            telefono_2=telefono_2,
                        ),
                    )
                    reporte.residentes_creados += 1
                    accion = "creado"
                mapa[documento] = residente.id
                reporte.detalles.append(
                    DetalleImportacionDTO(
                        "Residentes", fila.numero_fila, accion, f"{documento} · {nombre}"
                    )
                )
            except ErrorDominio as error:
                reporte.errores.append(ErrorImportacionDTO("Residentes", fila.numero_fila, error.mensaje))

        return mapa

    async def _procesar_bloques(
        self, unidad_negocio_id: int, datos: DatosImportacion, reporte: ReporteImportacionDTO
    ) -> dict[str, int]:
        mapa: dict[str, int] = {b.codigo: b.id for b in await self._bloques.listar(unidad_negocio_id)}
        caso_uso_crear = CrearBloqueUseCase(self._bloques)
        caso_uso_actualizar = ActualizarBloqueUseCase(self._bloques)

        for fila in datos.bloques:
            nombre, codigo = fila.obtener("nombre"), fila.obtener("codigo")
            if not nombre or not codigo:
                reporte.errores.append(
                    ErrorImportacionDTO("Bloques", fila.numero_fila, "nombre y codigo son obligatorios")
                )
                continue
            try:
                if codigo in mapa:
                    bloque = await caso_uso_actualizar.ejecutar(
                        unidad_negocio_id, mapa[codigo], ActualizarBloqueDTO(nombre=nombre, codigo=codigo)
                    )
                    reporte.bloques_actualizados += 1
                    accion = "actualizado"
                else:
                    bloque = await caso_uso_crear.ejecutar(
                        unidad_negocio_id, CrearBloqueDTO(nombre=nombre, codigo=codigo)
                    )
                    reporte.bloques_creados += 1
                    accion = "creado"
                mapa[codigo] = bloque.id
                reporte.detalles.append(
                    DetalleImportacionDTO("Bloques", fila.numero_fila, accion, f"{codigo} · {nombre}")
                )
            except ErrorDominio as error:
                reporte.errores.append(ErrorImportacionDTO("Bloques", fila.numero_fila, error.mensaje))

        return mapa

    async def _procesar_parqueaderos(
        self,
        unidad_negocio_id: int,
        datos: DatosImportacion,
        mapa_bloques: dict[str, int],
        mapa_residentes: dict[str, int],
        reporte: ReporteImportacionDTO,
    ) -> dict[tuple[str, str], int]:
        codigo_por_bloque_id = {bloque_id: codigo for codigo, bloque_id in mapa_bloques.items()}
        parqueaderos_existentes: dict[tuple[str, str], Parqueadero] = {}
        for bloque_id in mapa_bloques.values():
            codigo = codigo_por_bloque_id[bloque_id]
            for parqueadero in await self._parqueaderos.listar(unidad_negocio_id, bloque_id=bloque_id):
                parqueaderos_existentes[(codigo, parqueadero.numero)] = parqueadero

        mapa: dict[tuple[str, str], int] = {
            clave: p.id for clave, p in parqueaderos_existentes.items()
        }
        mapa_tipos_vehiculo = {t.codigo: t for t in await self._tipos_vehiculo.listar()}
        caso_uso_crear = CrearParqueaderoUseCase(
            self._parqueaderos, self._bloques, self._residentes, self._tipos_vehiculo
        )
        caso_uso_actualizar = ActualizarParqueaderoUseCase(
            self._parqueaderos, self._bloques, self._residentes, self._tipos_vehiculo, self._vehiculos
        )

        for fila in datos.parqueaderos:
            bloque_codigo = fila.obtener("bloque_codigo")
            numero = fila.obtener("numero")
            tipo_espacio = fila.obtener("tipo_espacio").upper()
            tipo_vehiculo_raw = fila.obtener("tipo_vehiculo").upper()
            capacidad_raw = fila.obtener("capacidad")
            propietario_documento = fila.obtener("propietario_documento") or None

            if not bloque_codigo or not numero or not tipo_espacio or not tipo_vehiculo_raw or not capacidad_raw:
                reporte.errores.append(
                    ErrorImportacionDTO(
                        "Parqueaderos",
                        fila.numero_fila,
                        "bloque_codigo, numero, tipo_espacio, tipo_vehiculo y capacidad son obligatorios",
                    )
                )
                continue
            if tipo_espacio not in (COMUNAL, PRIVADO):
                reporte.errores.append(
                    ErrorImportacionDTO(
                        "Parqueaderos", fila.numero_fila, "tipo_espacio inválido (usa COMUNAL o PRIVADO)"
                    )
                )
                continue
            if tipo_vehiculo_raw not in mapa_tipos_vehiculo:
                reporte.errores.append(
                    ErrorImportacionDTO(
                        "Parqueaderos",
                        fila.numero_fila,
                        f"tipo_vehiculo inválido: '{tipo_vehiculo_raw}' (usa CARRO o MOTO)",
                    )
                )
                continue
            try:
                capacidad = int(capacidad_raw)
            except ValueError:
                reporte.errores.append(
                    ErrorImportacionDTO(
                        "Parqueaderos", fila.numero_fila, "capacidad debe ser un número entero"
                    )
                )
                continue

            bloque_id = mapa_bloques.get(bloque_codigo)
            if bloque_id is None:
                reporte.errores.append(
                    ErrorImportacionDTO(
                        "Parqueaderos", fila.numero_fila, f"El bloque '{bloque_codigo}' no existe"
                    )
                )
                continue

            propietario_residente_id = None
            if propietario_documento:
                propietario_residente_id = mapa_residentes.get(propietario_documento)
                if propietario_residente_id is None:
                    reporte.errores.append(
                        ErrorImportacionDTO(
                            "Parqueaderos",
                            fila.numero_fila,
                            f"No existe un residente con documento '{propietario_documento}'",
                        )
                    )
                    continue

            clave = (bloque_codigo, numero)
            try:
                if clave in mapa:
                    activo_actual = parqueaderos_existentes[clave].activo
                    resultado = await caso_uso_actualizar.ejecutar(
                        unidad_negocio_id,
                        mapa[clave],
                        ActualizarParqueaderoDTO(
                            bloque_id=bloque_id,
                            numero=numero,
                            tipo_espacio=tipo_espacio,
                            tipo_vehiculo_id=mapa_tipos_vehiculo[tipo_vehiculo_raw].id,
                            capacidad=capacidad,
                            activo=activo_actual,
                            propietario_residente_id=propietario_residente_id,
                        ),
                    )
                    reporte.parqueaderos_actualizados += 1
                    accion = "actualizado"
                else:
                    resultado = await caso_uso_crear.ejecutar(
                        unidad_negocio_id,
                        CrearParqueaderoDTO(
                            bloque_id=bloque_id,
                            numero=numero,
                            tipo_espacio=tipo_espacio,
                            tipo_vehiculo_id=mapa_tipos_vehiculo[tipo_vehiculo_raw].id,
                            capacidad=capacidad,
                            propietario_residente_id=propietario_residente_id,
                        ),
                    )
                    reporte.parqueaderos_creados += 1
                    accion = "creado"
                mapa[clave] = resultado.parqueadero.id
                reporte.detalles.append(
                    DetalleImportacionDTO(
                        "Parqueaderos", fila.numero_fila, accion, f"{bloque_codigo} · {numero}"
                    )
                )
            except ErrorDominio as error:
                reporte.errores.append(ErrorImportacionDTO("Parqueaderos", fila.numero_fila, error.mensaje))

        return mapa

    async def _procesar_vehiculos(
        self,
        unidad_negocio_id: int,
        datos: DatosImportacion,
        mapa_residentes: dict[str, int],
        mapa_parqueaderos: dict[tuple[str, str], int],
        reporte: ReporteImportacionDTO,
    ) -> None:
        mapa_tipos_vehiculo = {t.codigo: t for t in await self._tipos_vehiculo.listar()}
        vehiculos_existentes = {
            str(v.placa): v
            for v in await self._vehiculos.listar(unidad_negocio_id, skip=0, limit=100000)
        }
        caso_uso_crear = RegistrarVehiculoUseCase(
            self._vehiculos, self._residentes, self._tipos_vehiculo, ValidadorReglasVehiculo()
        )
        caso_uso_actualizar = ActualizarVehiculoUseCase(
            self._vehiculos, self._residentes, self._tipos_vehiculo, ValidadorReglasVehiculo()
        )
        caso_uso_asignar_parqueadero = AsignarParqueaderoVehiculoUseCase(self._vehiculos, self._parqueaderos)

        for fila in datos.vehiculos:
            placa = fila.obtener("placa")
            tipo_raw = fila.obtener("tipo_vehiculo").upper()
            residente_documento = fila.obtener("residente_documento")
            bloque_codigo_veh = fila.obtener("bloque_codigo") or None
            parqueadero_numero_veh = fila.obtener("parqueadero_numero") or None

            if not placa or not residente_documento:
                reporte.errores.append(
                    ErrorImportacionDTO(
                        "Vehiculos", fila.numero_fila, "placa y residente_documento son obligatorios"
                    )
                )
                continue
            if tipo_raw not in mapa_tipos_vehiculo:
                reporte.errores.append(
                    ErrorImportacionDTO(
                        "Vehiculos", fila.numero_fila, f"tipo_vehiculo inválido: '{tipo_raw}' (usa CARRO o MOTO)"
                    )
                )
                continue
            residente_id = mapa_residentes.get(residente_documento)
            if residente_id is None:
                reporte.errores.append(
                    ErrorImportacionDTO(
                        "Vehiculos",
                        fila.numero_fila,
                        f"No existe un residente con documento '{residente_documento}'",
                    )
                )
                continue

            try:
                placa_normalizada = str(Placa(placa))
                existente = vehiculos_existentes.get(placa_normalizada)
                if existente is not None:
                    vehiculo = await caso_uso_actualizar.ejecutar(
                        unidad_negocio_id,
                        existente.id,
                        ActualizarVehiculoDTO(
                            placa=placa,
                            tipo_vehiculo_id=mapa_tipos_vehiculo[tipo_raw].id,
                            activo=existente.activo,
                        ),
                    )
                    reporte.vehiculos_actualizados += 1
                    accion = "actualizado"
                else:
                    vehiculo = await caso_uso_crear.ejecutar(
                        unidad_negocio_id,
                        CrearVehiculoDTO(
                            placa=placa,
                            tipo_vehiculo_id=mapa_tipos_vehiculo[tipo_raw].id,
                            residente_id=residente_id,
                        ),
                    )
                    reporte.vehiculos_creados += 1
                    accion = "creado"

                descripcion = f"{placa_normalizada} · {tipo_raw}"

                if bloque_codigo_veh and parqueadero_numero_veh:
                    parqueadero_id = mapa_parqueaderos.get((bloque_codigo_veh, parqueadero_numero_veh))
                    if parqueadero_id is None:
                        reporte.errores.append(
                            ErrorImportacionDTO(
                                "Vehiculos",
                                fila.numero_fila,
                                f"El parqueadero '{bloque_codigo_veh}/{parqueadero_numero_veh}' no existe",
                            )
                        )
                    else:
                        try:
                            await caso_uso_asignar_parqueadero.ejecutar(
                                unidad_negocio_id,
                                vehiculo.id,
                                AsignarParqueaderoVehiculoDTO(parqueadero_id=parqueadero_id),
                            )
                            descripcion += f" · Parqueadero {bloque_codigo_veh}/{parqueadero_numero_veh}"
                        except ErrorDominio as error_asignacion:
                            reporte.errores.append(
                                ErrorImportacionDTO(
                                    "Vehiculos",
                                    fila.numero_fila,
                                    f"No se pudo asignar el parqueadero: {error_asignacion.mensaje}",
                                )
                            )

                reporte.detalles.append(
                    DetalleImportacionDTO("Vehiculos", fila.numero_fila, accion, descripcion)
                )
            except ErrorDominio as error:
                reporte.errores.append(ErrorImportacionDTO("Vehiculos", fila.numero_fila, error.mensaje))
