"""Excepciones de dominio. Representan violaciones de reglas de negocio."""


class ErrorDominio(Exception):
    """Excepción base para todos los errores de dominio."""

    codigo: str = "ERROR_DOMINIO"

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


class PlacaInvalidaError(ErrorDominio):
    codigo = "PLACA_INVALIDA"


class PlacaDuplicadaError(ErrorDominio):
    codigo = "PLACA_DUPLICADA"


class ReglaVehiculoInvalidaError(ErrorDominio):
    codigo = "REGLA_VEHICULO_INVALIDA"


class DocumentoDuplicadoError(ErrorDominio):
    codigo = "DOCUMENTO_DUPLICADO"


class CorreoDuplicadoError(ErrorDominio):
    codigo = "CORREO_DUPLICADO"


class CodigoTorreDuplicadoError(ErrorDominio):
    codigo = "CODIGO_TORRE_DUPLICADO"


class SlugDuplicadoError(ErrorDominio):
    codigo = "SLUG_DUPLICADO"


class UnidadNegocioInactivaError(ErrorDominio):
    codigo = "UNIDAD_NEGOCIO_INACTIVA"


class AccesoUnidadNegocioInvalidoError(ErrorDominio):
    codigo = "ACCESO_UNIDAD_NEGOCIO_INVALIDO"


class ApartamentoDuplicadoError(ErrorDominio):
    codigo = "APARTAMENTO_DUPLICADO"


class EntidadNoEncontradaError(ErrorDominio):
    codigo = "ENTIDAD_NO_ENCONTRADA"


class CredencialesInvalidasError(ErrorDominio):
    codigo = "CREDENCIALES_INVALIDAS"


class UsuarioInactivoError(ErrorDominio):
    codigo = "USUARIO_INACTIVO"


class PermisoDenegadoError(ErrorDominio):
    codigo = "PERMISO_DENEGADO"


class TokenInvalidoError(ErrorDominio):
    codigo = "TOKEN_INVALIDO"


class CodigoBloqueDuplicadoError(ErrorDominio):
    codigo = "CODIGO_BLOQUE_DUPLICADO"


class ParqueaderoDuplicadoError(ErrorDominio):
    codigo = "PARQUEADERO_DUPLICADO"


class ParqueaderoLlenoError(ErrorDominio):
    codigo = "PARQUEADERO_LLENO"


class TipoVehiculoIncompatibleError(ErrorDominio):
    codigo = "TIPO_VEHICULO_INCOMPATIBLE"


class PropietarioInvalidoError(ErrorDominio):
    codigo = "PROPIETARIO_INVALIDO"


class DemasiadosIntentosError(ErrorDominio):
    codigo = "DEMASIADOS_INTENTOS"
