"""Enumeraciones del dominio de negocio."""
from enum import Enum


class NombreRol(str, Enum):
    ADMIN_PLATAFORMA = "ADMIN_PLATAFORMA"
    SUPER_ADMIN = "SUPER_ADMIN"
    VIGILANTE = "VIGILANTE"
