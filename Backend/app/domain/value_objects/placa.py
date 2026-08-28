"""Value object que representa una placa vehicular normalizada y validada."""
import re
from dataclasses import dataclass

from app.domain.exceptions.excepciones import PlacaInvalidaError

_PATRON_PLACA = re.compile(r"^[A-Z0-9]{5,7}$")


@dataclass(frozen=True)
class Placa:
    """Placa vehicular. Se normaliza a mayúsculas y sin espacios al crearse."""

    valor: str

    def __post_init__(self) -> None:
        normalizada = self._normalizar(self.valor)
        if not _PATRON_PLACA.match(normalizada):
            raise PlacaInvalidaError(
                f"La placa '{self.valor}' no tiene un formato válido"
            )
        object.__setattr__(self, "valor", normalizada)

    @staticmethod
    def _normalizar(valor: str) -> str:
        return re.sub(r"[\s-]", "", valor.strip().upper())

    def __str__(self) -> str:
        return self.valor
