"""Pruebas unitarias de normalización y validación del value object Placa."""
import pytest

from app.domain.exceptions.excepciones import PlacaInvalidaError
from app.domain.value_objects.placa import Placa


@pytest.mark.parametrize("valor", ["abc123", "ABC123", "Abc123", " abc123 ", "abc-123"])
def test_placas_equivalentes_se_normalizan_igual(valor: str) -> None:
    assert str(Placa(valor)) == "ABC123"


def test_placa_invalida_lanza_error() -> None:
    with pytest.raises(PlacaInvalidaError):
        Placa("AB")
