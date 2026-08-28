"""Configuración centralizada de logging para la aplicación."""
import logging
import sys


def configurar_logging(nivel: str = "INFO") -> None:
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )


def obtener_logger(nombre: str) -> logging.Logger:
    return logging.getLogger(nombre)
