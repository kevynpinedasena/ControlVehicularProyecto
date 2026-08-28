"""Pruebas unitarias de las reglas de negocio sobre vehículos por tipo de residente."""
import pytest

from app.domain.entities.tipo_residente import TipoResidente
from app.domain.entities.tipo_vehiculo import TipoVehiculo
from app.domain.entities.vehiculo import Vehiculo
from app.domain.exceptions.excepciones import ReglaVehiculoInvalidaError
from app.domain.services.validador_reglas_vehiculo import ValidadorReglasVehiculo
from app.domain.value_objects.placa import Placa

PROPIETARIO = TipoResidente(id=1, codigo="PROPIETARIO", nombre="Propietario")
ARRENDATARIO = TipoResidente(id=2, codigo="ARRENDATARIO", nombre="Arrendatario")
CARRO = TipoVehiculo(id=1, codigo="CARRO", nombre="Carro")
MOTO = TipoVehiculo(id=2, codigo="MOTO", nombre="Moto")


def _vehiculo(placa: str, tipo: TipoVehiculo) -> Vehiculo:
    return Vehiculo(id=1, placa=Placa(placa), tipo_vehiculo=tipo, residente_id=1, unidad_negocio_id=1)


@pytest.fixture
def validador() -> ValidadorReglasVehiculo:
    return ValidadorReglasVehiculo()


def test_propietario_puede_registrar_dos_motos(validador: ValidadorReglasVehiculo) -> None:
    validador.validar_nuevo_vehiculo(
        tipo_residente=PROPIETARIO,
        vehiculos_actuales=[_vehiculo("ABC12A", MOTO)],
        tipo_vehiculo_nuevo=MOTO,
    )


def test_propietario_puede_registrar_carro_y_moto(validador: ValidadorReglasVehiculo) -> None:
    validador.validar_nuevo_vehiculo(
        tipo_residente=PROPIETARIO,
        vehiculos_actuales=[_vehiculo("ABC123", CARRO)],
        tipo_vehiculo_nuevo=MOTO,
    )


def test_propietario_no_puede_registrar_dos_carros(validador: ValidadorReglasVehiculo) -> None:
    with pytest.raises(ReglaVehiculoInvalidaError):
        validador.validar_nuevo_vehiculo(
            tipo_residente=PROPIETARIO,
            vehiculos_actuales=[_vehiculo("ABC123", CARRO)],
            tipo_vehiculo_nuevo=CARRO,
        )


def test_propietario_no_puede_registrar_mas_de_dos_vehiculos(
    validador: ValidadorReglasVehiculo,
) -> None:
    with pytest.raises(ReglaVehiculoInvalidaError):
        validador.validar_nuevo_vehiculo(
            tipo_residente=PROPIETARIO,
            vehiculos_actuales=[
                _vehiculo("ABC12A", MOTO),
                _vehiculo("XYZ34B", MOTO),
            ],
            tipo_vehiculo_nuevo=MOTO,
        )


def test_arrendatario_puede_registrar_un_vehiculo(validador: ValidadorReglasVehiculo) -> None:
    validador.validar_nuevo_vehiculo(
        tipo_residente=ARRENDATARIO,
        vehiculos_actuales=[],
        tipo_vehiculo_nuevo=CARRO,
    )


def test_arrendatario_no_puede_registrar_mas_de_un_vehiculo(
    validador: ValidadorReglasVehiculo,
) -> None:
    with pytest.raises(ReglaVehiculoInvalidaError):
        validador.validar_nuevo_vehiculo(
            tipo_residente=ARRENDATARIO,
            vehiculos_actuales=[_vehiculo("ABC123", CARRO)],
            tipo_vehiculo_nuevo=MOTO,
        )


def test_cambio_de_propietario_a_arrendatario_revalida_vehiculos(
    validador: ValidadorReglasVehiculo,
) -> None:
    with pytest.raises(ReglaVehiculoInvalidaError):
        validador.validar_cambio_tipo_residente(
            nuevo_tipo_residente=ARRENDATARIO,
            vehiculos_actuales=[
                _vehiculo("ABC12A", MOTO),
                _vehiculo("XYZ34B", MOTO),
            ],
        )