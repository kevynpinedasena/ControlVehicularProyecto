"""Esquema inicial multi-tenant: unidades de negocio, roles, usuarios, torres,
apartamentos, residentes y vehículos.

Revision ID: 202608240001
Revises:
Create Date: 2026-08-24

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202608240001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

nombre_rol_enum = sa.Enum("ADMIN_PLATAFORMA", "SUPER_ADMIN", "VIGILANTE", name="nombre_rol_enum")
tipo_residente_enum = sa.Enum("PROPIETARIO", "ARRENDATARIO", name="tipo_residente_enum")
tipo_vehiculo_enum = sa.Enum("CARRO", "MOTO", name="tipo_vehiculo_enum")


def upgrade() -> None:
    op.create_table(
        "unidades_negocio",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(150), nullable=False),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("color_primario", sa.String(20), nullable=False, server_default="#2563eb"),
        sa.Column("color_secundario", sa.String(20), nullable=False, server_default="#1e293b"),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("slug", name="uq_unidades_negocio_slug"),
    )
    op.create_index("ix_unidades_negocio_slug", "unidades_negocio", ["slug"])

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", nombre_rol_enum, nullable=False, unique=True),
    )

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(150), nullable=False),
        sa.Column("correo", sa.String(150), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("rol_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column(
            "unidad_negocio_id", sa.Integer(), sa.ForeignKey("unidades_negocio.id"), nullable=True
        ),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("correo", name="uq_usuarios_correo"),
    )
    op.create_index("ix_usuarios_correo", "usuarios", ["correo"])

    op.create_table(
        "torres",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("codigo", sa.String(20), nullable=False),
        sa.Column(
            "unidad_negocio_id", sa.Integer(), sa.ForeignKey("unidades_negocio.id"), nullable=False
        ),
        sa.UniqueConstraint("unidad_negocio_id", "codigo", name="uq_unidad_codigo_torre"),
    )
    op.create_index("ix_torres_codigo", "torres", ["codigo"])

    op.create_table(
        "apartamentos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("torre_id", sa.Integer(), sa.ForeignKey("torres.id"), nullable=False),
        sa.Column("numero", sa.String(20), nullable=False),
        sa.Column(
            "unidad_negocio_id", sa.Integer(), sa.ForeignKey("unidades_negocio.id"), nullable=False
        ),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("torre_id", "numero", name="uq_torre_numero"),
    )

    op.create_table(
        "residentes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(150), nullable=False),
        sa.Column("documento", sa.String(30), nullable=False),
        sa.Column("tipo_residente", tipo_residente_enum, nullable=False),
        sa.Column("apartamento_id", sa.Integer(), sa.ForeignKey("apartamentos.id"), nullable=False),
        sa.Column(
            "unidad_negocio_id", sa.Integer(), sa.ForeignKey("unidades_negocio.id"), nullable=False
        ),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("unidad_negocio_id", "documento", name="uq_unidad_documento_residente"),
    )
    op.create_index("ix_residentes_documento", "residentes", ["documento"])

    op.create_table(
        "vehiculos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("placa", sa.String(10), nullable=False),
        sa.Column("tipo_vehiculo", tipo_vehiculo_enum, nullable=False),
        sa.Column("residente_id", sa.Integer(), sa.ForeignKey("residentes.id"), nullable=False),
        sa.Column(
            "unidad_negocio_id", sa.Integer(), sa.ForeignKey("unidades_negocio.id"), nullable=False
        ),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("unidad_negocio_id", "placa", name="uq_unidad_placa_vehiculo"),
    )
    op.create_index("ix_vehiculos_placa_busqueda", "vehiculos", ["placa"])


def downgrade() -> None:
    op.drop_table("vehiculos")
    op.drop_table("residentes")
    op.drop_table("apartamentos")
    op.drop_table("torres")
    op.drop_table("usuarios")
    op.drop_table("roles")
    op.drop_table("unidades_negocio")

    tipo_vehiculo_enum.drop(op.get_bind(), checkfirst=True)
    tipo_residente_enum.drop(op.get_bind(), checkfirst=True)
    nombre_rol_enum.drop(op.get_bind(), checkfirst=True)
