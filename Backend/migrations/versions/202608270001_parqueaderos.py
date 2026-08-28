"""Gestión de parqueaderos: bloques, parqueaderos (comunales/privados, tipo de
vehículo y capacidad) y la asignación opcional de un vehículo a un parqueadero.

Revision ID: 202608270001
Revises: 202608260001
Create Date: 2026-08-27

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202608270001"
down_revision: Union[str, None] = "202608260001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tipo_espacio_parqueadero_enum = sa.Enum(
    "COMUNAL", "PRIVADO", name="tipo_espacio_parqueadero_enum"
)


def upgrade() -> None:
    op.create_table(
        "bloques",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("codigo", sa.String(20), nullable=False),
        sa.Column(
            "unidad_negocio_id", sa.Integer(), sa.ForeignKey("unidades_negocio.id"), nullable=False
        ),
        sa.UniqueConstraint("unidad_negocio_id", "codigo", name="uq_unidad_codigo_bloque"),
    )
    op.create_index("ix_bloques_codigo", "bloques", ["codigo"])

    op.create_table(
        "parqueaderos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bloque_id", sa.Integer(), sa.ForeignKey("bloques.id"), nullable=False),
        sa.Column("numero", sa.String(20), nullable=False),
        sa.Column("tipo_espacio", tipo_espacio_parqueadero_enum, nullable=False),
        sa.Column(
            "tipo_vehiculo_id", sa.Integer(), sa.ForeignKey("tipos_vehiculo.id"), nullable=False
        ),
        sa.Column("capacidad", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "propietario_residente_id",
            sa.Integer(),
            sa.ForeignKey("residentes.id"),
            nullable=True,
        ),
        sa.Column(
            "unidad_negocio_id", sa.Integer(), sa.ForeignKey("unidades_negocio.id"), nullable=False
        ),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("bloque_id", "numero", name="uq_bloque_numero"),
    )

    op.add_column("vehiculos", sa.Column("parqueadero_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_vehiculos_parqueadero", "vehiculos", "parqueaderos", ["parqueadero_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_vehiculos_parqueadero", "vehiculos", type_="foreignkey")
    op.drop_column("vehiculos", "parqueadero_id")

    op.drop_table("parqueaderos")

    op.drop_index("ix_bloques_codigo", table_name="bloques")
    op.drop_table("bloques")

    tipo_espacio_parqueadero_enum.drop(op.get_bind(), checkfirst=True)