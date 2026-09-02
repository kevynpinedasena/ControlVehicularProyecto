"""Modelos ORM (SQLAlchemy) que mapean las tablas de PostgreSQL."""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.enums import NombreRol
from app.infrastructure.database.base import Base


class UnidadNegocioModel(Base):
    __tablename__ = "unidades_negocio"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    color_primario: Mapped[str] = mapped_column(String(20), nullable=False, default="#2563eb")
    color_secundario: Mapped[str] = mapped_column(String(20), nullable=False, default="#1e293b")
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    usuarios: Mapped[list["UsuarioModel"]] = relationship(back_populates="unidad_negocio")
    torres: Mapped[list["TorreModel"]] = relationship(back_populates="unidad_negocio")


class RolModel(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[NombreRol] = mapped_column(
        Enum(NombreRol, name="nombre_rol_enum"), unique=True, nullable=False
    )

    usuarios: Mapped[list["UsuarioModel"]] = relationship(back_populates="rol")


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    correo: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    unidad_negocio_id: Mapped[int | None] = mapped_column(
        ForeignKey("unidades_negocio.id"), nullable=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    rol: Mapped["RolModel"] = relationship(back_populates="usuarios")
    unidad_negocio: Mapped["UnidadNegocioModel | None"] = relationship(back_populates="usuarios")


class TorreModel(Base):
    __tablename__ = "torres"
    __table_args__ = (UniqueConstraint("unidad_negocio_id", "codigo", name="uq_unidad_codigo_torre"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    unidad_negocio_id: Mapped[int] = mapped_column(
        ForeignKey("unidades_negocio.id"), nullable=False
    )

    unidad_negocio: Mapped["UnidadNegocioModel"] = relationship(back_populates="torres")
    apartamentos: Mapped[list["ApartamentoModel"]] = relationship(
        back_populates="torre", cascade="all, delete-orphan"
    )


class ApartamentoModel(Base):
    __tablename__ = "apartamentos"
    __table_args__ = (UniqueConstraint("torre_id", "numero", name="uq_torre_numero"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    torre_id: Mapped[int] = mapped_column(ForeignKey("torres.id"), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    unidad_negocio_id: Mapped[int] = mapped_column(
        ForeignKey("unidades_negocio.id"), nullable=False
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    torre: Mapped["TorreModel"] = relationship(back_populates="apartamentos")
    residentes: Mapped[list["ResidenteModel"]] = relationship(back_populates="apartamento")


class TipoVehiculoModel(Base):
    __tablename__ = "tipos_vehiculo"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)


class TipoResidenteModel(Base):
    __tablename__ = "tipos_residente"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)


class BloqueModel(Base):
    __tablename__ = "bloques"
    __table_args__ = (UniqueConstraint("unidad_negocio_id", "codigo", name="uq_unidad_codigo_bloque"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    unidad_negocio_id: Mapped[int] = mapped_column(
        ForeignKey("unidades_negocio.id"), nullable=False
    )

    parqueaderos: Mapped[list["ParqueaderoModel"]] = relationship(
        back_populates="bloque", cascade="all, delete-orphan"
    )


class ParqueaderoModel(Base):
    __tablename__ = "parqueaderos"
    __table_args__ = (UniqueConstraint("bloque_id", "numero", name="uq_bloque_numero"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    bloque_id: Mapped[int] = mapped_column(ForeignKey("bloques.id"), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    tipo_espacio: Mapped[str] = mapped_column(
        Enum("COMUNAL", "PRIVADO", name="tipo_espacio_parqueadero_enum"), nullable=False
    )
    tipo_vehiculo_id: Mapped[int] = mapped_column(
        ForeignKey("tipos_vehiculo.id"), nullable=False
    )
    tipo_vehiculo_rel: Mapped["TipoVehiculoModel"] = relationship(lazy="joined")
    capacidad: Mapped[int] = mapped_column(nullable=False, default=1)
    propietario_residente_id: Mapped[int | None] = mapped_column(
        ForeignKey("residentes.id"), nullable=True
    )
    unidad_negocio_id: Mapped[int] = mapped_column(
        ForeignKey("unidades_negocio.id"), nullable=False
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    bloque: Mapped["BloqueModel"] = relationship(back_populates="parqueaderos")


class ResidenteModel(Base):
    __tablename__ = "residentes"
    __table_args__ = (
        UniqueConstraint("unidad_negocio_id", "documento", name="uq_unidad_documento_residente"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    documento: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    tipo_residente_id: Mapped[int] = mapped_column(
        ForeignKey("tipos_residente.id"), nullable=False
    )
    tipo_residente_rel: Mapped["TipoResidenteModel"] = relationship(lazy="joined")
    apartamento_id: Mapped[int] = mapped_column(ForeignKey("apartamentos.id"), nullable=False)
    unidad_negocio_id: Mapped[int] = mapped_column(
        ForeignKey("unidades_negocio.id"), nullable=False
    )
    telefono_1: Mapped[str | None] = mapped_column(String(30), nullable=True)
    telefono_2: Mapped[str | None] = mapped_column(String(30), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    apartamento: Mapped["ApartamentoModel"] = relationship(back_populates="residentes")
    vehiculos: Mapped[list["VehiculoModel"]] = relationship(
        back_populates="residente", cascade="all, delete-orphan"
    )


class VehiculoModel(Base):
    __tablename__ = "vehiculos"
    __table_args__ = (
        UniqueConstraint("unidad_negocio_id", "placa", name="uq_unidad_placa_vehiculo"),
        Index("ix_vehiculos_placa_busqueda", "placa"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    placa: Mapped[str] = mapped_column(String(10), nullable=False)
    tipo_vehiculo_id: Mapped[int] = mapped_column(
        ForeignKey("tipos_vehiculo.id"), nullable=False
    )
    tipo_vehiculo_rel: Mapped["TipoVehiculoModel"] = relationship(lazy="joined")
    residente_id: Mapped[int] = mapped_column(ForeignKey("residentes.id"), nullable=False)
    parqueadero_id: Mapped[int | None] = mapped_column(
        ForeignKey("parqueaderos.id"), nullable=True
    )
    unidad_negocio_id: Mapped[int] = mapped_column(
        ForeignKey("unidades_negocio.id"), nullable=False
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    residente: Mapped["ResidenteModel"] = relationship(back_populates="vehiculos")
