"""Servicio de dominio que valida las reglas de negocio sobre vehículos y residentes.

Reglas:
    - PROPIETARIO: máximo 2 vehículos, y nunca 2 carros.
    - ARRENDATARIO: máximo 1 vehículo.
"""
from app.domain.entities.tipo_residente import TipoResidente
from app.domain.entities.tipo_vehiculo import TipoVehiculo
from app.domain.entities.vehiculo import Vehiculo
from app.domain.exceptions.excepciones import ReglaVehiculoInvalidaError

CODIGO_CARRO = "CARRO"
CODIGO_PROPIETARIO = "PROPIETARIO"
CODIGO_ARRENDATARIO = "ARRENDATARIO"

LIMITE_VEHICULOS = {
    CODIGO_PROPIETARIO: 2,
    CODIGO_ARRENDATARIO: 1,
}


class ValidadorReglasVehiculo:
    """Valida si un vehículo puede agregarse a un residente según su tipo."""

    def validar_nuevo_vehiculo(
        self,
        tipo_residente: TipoResidente,
        vehiculos_actuales: list[Vehiculo],
        tipo_vehiculo_nuevo: TipoVehiculo,
    ) -> None:
        vehiculos_resultantes = [
            v.tipo_vehiculo for v in vehiculos_actuales
        ] + [tipo_vehiculo_nuevo]
        self._validar_conjunto(tipo_residente, vehiculos_resultantes)

    def validar_cambio_tipo_residente(
        self,
        nuevo_tipo_residente: TipoResidente,
        vehiculos_actuales: list[Vehiculo],
    ) -> None:
        vehiculos_resultantes = [v.tipo_vehiculo for v in vehiculos_actuales]
        self._validar_conjunto(nuevo_tipo_residente, vehiculos_resultantes)

    def _validar_conjunto(
        self,
        tipo_residente: TipoResidente,
        tipos_vehiculo: list[TipoVehiculo],
    ) -> None:
        limite = LIMITE_VEHICULOS[tipo_residente.codigo]

        if len(tipos_vehiculo) > limite:
            raise ReglaVehiculoInvalidaError(
                f"Un residente de tipo {tipo_residente.codigo} no puede tener "
                f"más de {limite} vehículo(s) registrado(s)"
            )

        total_carros = sum(1 for t in tipos_vehiculo if t.codigo == CODIGO_CARRO)

        if total_carros > 1:
            raise ReglaVehiculoInvalidaError(
                "No se puede registrar más de un carro para el mismo residente"
            )

        if tipo_residente.codigo == CODIGO_ARRENDATARIO and len(tipos_vehiculo) > 1:
            raise ReglaVehiculoInvalidaError(
                "Un arrendatario no puede registrar más de 1 vehículo"
            )
