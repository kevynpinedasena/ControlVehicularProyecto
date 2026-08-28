"""Proveedores de casos de uso: ensamblan repositorios y servicios de dominio."""
from typing import Annotated

from fastapi import Depends

from app.application.use_cases.auth_use_cases import (
    AutenticarUsuarioUseCase,
    ObtenerUsuarioActualUseCase,
    RefrescarTokenUseCase,
)
from app.application.use_cases.importacion_use_cases import ImportarDatosMasivosUseCase
from app.application.use_cases.parqueadero_use_cases import (
    ActualizarBloqueUseCase,
    ActualizarParqueaderoUseCase,
    CrearBloqueUseCase,
    CrearParqueaderoUseCase,
    EliminarBloqueUseCase,
    EliminarParqueaderoUseCase,
    ListarBloquesUseCase,
    ListarParqueaderosUseCase,
)
from app.application.use_cases.residente_use_cases import (
    ActualizarResidenteUseCase,
    CrearResidenteUseCase,
    EliminarResidenteUseCase,
    ListarResidentesUseCase,
    ObtenerResidenteUseCase,
)
from app.application.use_cases.tipo_use_cases import (
    ListarTiposResidenteUseCase,
    ListarTiposVehiculoUseCase,
)
from app.application.use_cases.ubicacion_use_cases import (
    ActualizarApartamentoUseCase,
    ActualizarTorreUseCase,
    CrearApartamentoUseCase,
    CrearTorreUseCase,
    EliminarApartamentoUseCase,
    EliminarTorreUseCase,
    ListarApartamentosUseCase,
    ListarTorresUseCase,
)
from app.application.use_cases.unidad_negocio_use_cases import (
    ActualizarLogoUnidadNegocioUseCase,
    ActualizarUnidadNegocioUseCase,
    CrearUnidadNegocioUseCase,
    ListarUnidadesNegocioUseCase,
    ObtenerUnidadNegocioPublicaUseCase,
)
from app.application.use_cases.usuario_use_cases import (
    ActualizarUsuarioUseCase,
    CambiarEstadoUsuarioUseCase,
    CrearUsuarioUseCase,
    ListarUsuariosDeUnidadUseCase,
    ListarUsuariosUseCase,
    ObtenerUsuarioUseCase,
    RestablecerPasswordUsuarioUseCase,
)
from app.application.use_cases.vehiculo_use_cases import (
    ActualizarVehiculoUseCase,
    AsignarParqueaderoVehiculoUseCase,
    ConsultarPlacaUseCase,
    EliminarVehiculoUseCase,
    ListarVehiculosUseCase,
    ObtenerVehiculoUseCase,
    RegistrarVehiculoUseCase,
)
from app.domain.repositories.apartamento_repository import IApartamentoRepository
from app.domain.repositories.bloque_repository import IBloqueRepository
from app.domain.repositories.parqueadero_repository import IParqueaderoRepository
from app.domain.repositories.residente_repository import IResidenteRepository
from app.domain.repositories.tipo_residente_repository import ITipoResidenteRepository
from app.domain.repositories.tipo_vehiculo_repository import ITipoVehiculoRepository
from app.domain.repositories.torre_repository import ITorreRepository
from app.domain.repositories.unidad_negocio_repository import IUnidadNegocioRepository
from app.domain.repositories.usuario_repository import IUsuarioRepository
from app.domain.repositories.vehiculo_repository import IVehiculoRepository
from app.domain.services.validador_reglas_vehiculo import ValidadorReglasVehiculo
from app.presentation.dependencies.repositorios import (
    obtener_apartamento_repository,
    obtener_bloque_repository,
    obtener_parqueadero_repository,
    obtener_residente_repository,
    obtener_tipo_residente_repository,
    obtener_tipo_vehiculo_repository,
    obtener_torre_repository,
    obtener_unidad_negocio_repository,
    obtener_usuario_repository,
    obtener_vehiculo_repository,
)

UsuarioRepo = Annotated[IUsuarioRepository, Depends(obtener_usuario_repository)]
TorreRepo = Annotated[ITorreRepository, Depends(obtener_torre_repository)]
ApartamentoRepo = Annotated[IApartamentoRepository, Depends(obtener_apartamento_repository)]
ResidenteRepo = Annotated[IResidenteRepository, Depends(obtener_residente_repository)]
VehiculoRepo = Annotated[IVehiculoRepository, Depends(obtener_vehiculo_repository)]
UnidadNegocioRepo = Annotated[IUnidadNegocioRepository, Depends(obtener_unidad_negocio_repository)]
TipoVehiculoRepo = Annotated[ITipoVehiculoRepository, Depends(obtener_tipo_vehiculo_repository)]
TipoResidenteRepo = Annotated[ITipoResidenteRepository, Depends(obtener_tipo_residente_repository)]
BloqueRepo = Annotated[IBloqueRepository, Depends(obtener_bloque_repository)]
ParqueaderoRepo = Annotated[IParqueaderoRepository, Depends(obtener_parqueadero_repository)]


def _validador() -> ValidadorReglasVehiculo:
    return ValidadorReglasVehiculo()


# --- Autenticación ---
def caso_uso_autenticar(usuarios: UsuarioRepo, unidades: UnidadNegocioRepo) -> AutenticarUsuarioUseCase:
    return AutenticarUsuarioUseCase(usuarios, unidades)


def caso_uso_refrescar_token(usuarios: UsuarioRepo) -> RefrescarTokenUseCase:
    return RefrescarTokenUseCase(usuarios)


def caso_uso_usuario_actual(usuarios: UsuarioRepo) -> ObtenerUsuarioActualUseCase:
    return ObtenerUsuarioActualUseCase(usuarios)


# --- Usuarios ---
def caso_uso_crear_usuario(usuarios: UsuarioRepo) -> CrearUsuarioUseCase:
    return CrearUsuarioUseCase(usuarios)


def caso_uso_listar_usuarios(usuarios: UsuarioRepo) -> ListarUsuariosUseCase:
    return ListarUsuariosUseCase(usuarios)


def caso_uso_obtener_usuario(usuarios: UsuarioRepo) -> ObtenerUsuarioUseCase:
    return ObtenerUsuarioUseCase(usuarios)


def caso_uso_actualizar_usuario(usuarios: UsuarioRepo) -> ActualizarUsuarioUseCase:
    return ActualizarUsuarioUseCase(usuarios)


def caso_uso_cambiar_estado_usuario(usuarios: UsuarioRepo) -> CambiarEstadoUsuarioUseCase:
    return CambiarEstadoUsuarioUseCase(usuarios)


def caso_uso_listar_usuarios_de_unidad(usuarios: UsuarioRepo) -> ListarUsuariosDeUnidadUseCase:
    return ListarUsuariosDeUnidadUseCase(usuarios)


def caso_uso_restablecer_password_usuario(usuarios: UsuarioRepo) -> RestablecerPasswordUsuarioUseCase:
    return RestablecerPasswordUsuarioUseCase(usuarios)


# --- Torres ---
def caso_uso_crear_torre(torres: TorreRepo) -> CrearTorreUseCase:
    return CrearTorreUseCase(torres)


def caso_uso_listar_torres(torres: TorreRepo) -> ListarTorresUseCase:
    return ListarTorresUseCase(torres)


def caso_uso_actualizar_torre(torres: TorreRepo) -> ActualizarTorreUseCase:
    return ActualizarTorreUseCase(torres)


def caso_uso_eliminar_torre(torres: TorreRepo) -> EliminarTorreUseCase:
    return EliminarTorreUseCase(torres)


# --- Apartamentos ---
def caso_uso_crear_apartamento(
    apartamentos: ApartamentoRepo, torres: TorreRepo
) -> CrearApartamentoUseCase:
    return CrearApartamentoUseCase(apartamentos, torres)


def caso_uso_listar_apartamentos(apartamentos: ApartamentoRepo) -> ListarApartamentosUseCase:
    return ListarApartamentosUseCase(apartamentos)


def caso_uso_actualizar_apartamento(
    apartamentos: ApartamentoRepo, torres: TorreRepo
) -> ActualizarApartamentoUseCase:
    return ActualizarApartamentoUseCase(apartamentos, torres)


def caso_uso_eliminar_apartamento(apartamentos: ApartamentoRepo) -> EliminarApartamentoUseCase:
    return EliminarApartamentoUseCase(apartamentos)


# --- Residentes ---
def caso_uso_crear_residente(
    residentes: ResidenteRepo, apartamentos: ApartamentoRepo, tipos_residente: TipoResidenteRepo
) -> CrearResidenteUseCase:
    return CrearResidenteUseCase(residentes, apartamentos, tipos_residente)


def caso_uso_listar_residentes(residentes: ResidenteRepo) -> ListarResidentesUseCase:
    return ListarResidentesUseCase(residentes)


def caso_uso_obtener_residente(residentes: ResidenteRepo) -> ObtenerResidenteUseCase:
    return ObtenerResidenteUseCase(residentes)


def caso_uso_actualizar_residente(
    residentes: ResidenteRepo,
    apartamentos: ApartamentoRepo,
    vehiculos: VehiculoRepo,
    tipos_residente: TipoResidenteRepo,
) -> ActualizarResidenteUseCase:
    return ActualizarResidenteUseCase(residentes, apartamentos, vehiculos, tipos_residente, _validador())


def caso_uso_eliminar_residente(residentes: ResidenteRepo) -> EliminarResidenteUseCase:
    return EliminarResidenteUseCase(residentes)


# --- Vehículos ---
def caso_uso_registrar_vehiculo(
    vehiculos: VehiculoRepo, residentes: ResidenteRepo, tipos_vehiculo: TipoVehiculoRepo
) -> RegistrarVehiculoUseCase:
    return RegistrarVehiculoUseCase(vehiculos, residentes, tipos_vehiculo, _validador())


def caso_uso_listar_vehiculos(vehiculos: VehiculoRepo) -> ListarVehiculosUseCase:
    return ListarVehiculosUseCase(vehiculos)


def caso_uso_obtener_vehiculo(vehiculos: VehiculoRepo) -> ObtenerVehiculoUseCase:
    return ObtenerVehiculoUseCase(vehiculos)


def caso_uso_actualizar_vehiculo(
    vehiculos: VehiculoRepo, residentes: ResidenteRepo, tipos_vehiculo: TipoVehiculoRepo
) -> ActualizarVehiculoUseCase:
    return ActualizarVehiculoUseCase(vehiculos, residentes, tipos_vehiculo, _validador())


def caso_uso_eliminar_vehiculo(vehiculos: VehiculoRepo) -> EliminarVehiculoUseCase:
    return EliminarVehiculoUseCase(vehiculos)


def caso_uso_asignar_parqueadero_vehiculo(
    vehiculos: VehiculoRepo, parqueaderos: ParqueaderoRepo
) -> AsignarParqueaderoVehiculoUseCase:
    return AsignarParqueaderoVehiculoUseCase(vehiculos, parqueaderos)


def caso_uso_consultar_placa(
    vehiculos: VehiculoRepo,
    residentes: ResidenteRepo,
    apartamentos: ApartamentoRepo,
    torres: TorreRepo,
    parqueaderos: ParqueaderoRepo,
    bloques: BloqueRepo,
) -> ConsultarPlacaUseCase:
    return ConsultarPlacaUseCase(vehiculos, residentes, apartamentos, torres, parqueaderos, bloques)


# --- Unidades de negocio (plataforma) ---
def caso_uso_crear_unidad_negocio(
    unidades: UnidadNegocioRepo, usuarios: UsuarioRepo
) -> CrearUnidadNegocioUseCase:
    return CrearUnidadNegocioUseCase(unidades, usuarios)


def caso_uso_listar_unidades_negocio(unidades: UnidadNegocioRepo) -> ListarUnidadesNegocioUseCase:
    return ListarUnidadesNegocioUseCase(unidades)


def caso_uso_obtener_unidad_negocio_publica(
    unidades: UnidadNegocioRepo,
) -> ObtenerUnidadNegocioPublicaUseCase:
    return ObtenerUnidadNegocioPublicaUseCase(unidades)


def caso_uso_actualizar_unidad_negocio(unidades: UnidadNegocioRepo) -> ActualizarUnidadNegocioUseCase:
    return ActualizarUnidadNegocioUseCase(unidades)


def caso_uso_actualizar_logo_unidad_negocio(
    unidades: UnidadNegocioRepo,
) -> ActualizarLogoUnidadNegocioUseCase:
    return ActualizarLogoUnidadNegocioUseCase(unidades)


# --- Carga masiva ---
def caso_uso_importar_datos_masivos(
    torres: TorreRepo,
    apartamentos: ApartamentoRepo,
    residentes: ResidenteRepo,
    vehiculos: VehiculoRepo,
    tipos_residente: TipoResidenteRepo,
    tipos_vehiculo: TipoVehiculoRepo,
    bloques: BloqueRepo,
    parqueaderos: ParqueaderoRepo,
) -> ImportarDatosMasivosUseCase:
    return ImportarDatosMasivosUseCase(
        torres, apartamentos, residentes, vehiculos, tipos_residente, tipos_vehiculo, bloques, parqueaderos
    )


# --- Catálogos de tipo ---
def caso_uso_listar_tipos_vehiculo(tipos_vehiculo: TipoVehiculoRepo) -> ListarTiposVehiculoUseCase:
    return ListarTiposVehiculoUseCase(tipos_vehiculo)


def caso_uso_listar_tipos_residente(tipos_residente: TipoResidenteRepo) -> ListarTiposResidenteUseCase:
    return ListarTiposResidenteUseCase(tipos_residente)


# --- Bloques ---
def caso_uso_crear_bloque(bloques: BloqueRepo) -> CrearBloqueUseCase:
    return CrearBloqueUseCase(bloques)


def caso_uso_listar_bloques(bloques: BloqueRepo) -> ListarBloquesUseCase:
    return ListarBloquesUseCase(bloques)


def caso_uso_actualizar_bloque(bloques: BloqueRepo) -> ActualizarBloqueUseCase:
    return ActualizarBloqueUseCase(bloques)


def caso_uso_eliminar_bloque(bloques: BloqueRepo) -> EliminarBloqueUseCase:
    return EliminarBloqueUseCase(bloques)


# --- Parqueaderos ---
def caso_uso_crear_parqueadero(
    parqueaderos: ParqueaderoRepo,
    bloques: BloqueRepo,
    residentes: ResidenteRepo,
    tipos_vehiculo: TipoVehiculoRepo,
) -> CrearParqueaderoUseCase:
    return CrearParqueaderoUseCase(parqueaderos, bloques, residentes, tipos_vehiculo)


def caso_uso_listar_parqueaderos(
    parqueaderos: ParqueaderoRepo, vehiculos: VehiculoRepo
) -> ListarParqueaderosUseCase:
    return ListarParqueaderosUseCase(parqueaderos, vehiculos)


def caso_uso_actualizar_parqueadero(
    parqueaderos: ParqueaderoRepo,
    bloques: BloqueRepo,
    residentes: ResidenteRepo,
    tipos_vehiculo: TipoVehiculoRepo,
    vehiculos: VehiculoRepo,
) -> ActualizarParqueaderoUseCase:
    return ActualizarParqueaderoUseCase(parqueaderos, bloques, residentes, tipos_vehiculo, vehiculos)


def caso_uso_eliminar_parqueadero(parqueaderos: ParqueaderoRepo) -> EliminarParqueaderoUseCase:
    return EliminarParqueaderoUseCase(parqueaderos)
