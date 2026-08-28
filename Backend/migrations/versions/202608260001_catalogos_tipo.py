"""Convierte tipo_residente/tipo_vehiculo de enums a catálogos reales en BD
(tablas tipos_residente / tipos_vehiculo), sembrados con ids fijos.

Revision ID: 202608260001
Revises: 202608250001
Create Date: 2026-08-26

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202608260001"
down_revision: Union[str, None] = "202608250001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tipo_residente_enum = sa.Enum("PROPIETARIO", "ARRENDATARIO", name="tipo_residente_enum")
tipo_vehiculo_enum = sa.Enum("CARRO", "MOTO", name="tipo_vehiculo_enum")


def upgrade() -> None:
    op.create_table(
        "tipos_vehiculo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("codigo", sa.String(20), nullable=False),
        sa.Column("nombre", sa.String(50), nullable=False),
        sa.UniqueConstraint("codigo", name="uq_tipos_vehiculo_codigo"),
    )
    op.create_table(
        "tipos_residente",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("codigo", sa.String(20), nullable=False),
        sa.Column("nombre", sa.String(50), nullable=False),
        sa.UniqueConstraint("codigo", name="uq_tipos_residente_codigo"),
    )

    tabla_tipos_vehiculo = sa.table(
        "tipos_vehiculo", sa.column("id"), sa.column("codigo"), sa.column("nombre")
    )
    op.bulk_insert(
        tabla_tipos_vehiculo,
        [
            {"id": 1, "codigo": "CARRO", "nombre": "Carro"},
            {"id": 2, "codigo": "MOTO", "nombre": "Moto"},
        ],
    )

    tabla_tipos_residente = sa.table(
        "tipos_residente", sa.column("id"), sa.column("codigo"), sa.column("nombre")
    )
    op.bulk_insert(
        tabla_tipos_residente,
        [
            {"id": 1, "codigo": "PROPIETARIO", "nombre": "Propietario"},
            {"id": 2, "codigo": "ARRENDATARIO", "nombre": "Arrendatario"},
        ],
    )

    op.add_column("vehiculos", sa.Column("tipo_vehiculo_id", sa.Integer(), nullable=True))
    op.execute(
        """
        UPDATE vehiculos SET tipo_vehiculo_id = CASE tipo_vehiculo
            WHEN 'CARRO' THEN 1
            WHEN 'MOTO' THEN 2
        END
        """
    )
    op.alter_column("vehiculos", "tipo_vehiculo_id", nullable=False)
    op.create_foreign_key(
        "fk_vehiculos_tipo_vehiculo", "vehiculos", "tipos_vehiculo", ["tipo_vehiculo_id"], ["id"]
    )
    op.drop_column("vehiculos", "tipo_vehiculo")

    op.add_column("residentes", sa.Column("tipo_residente_id", sa.Integer(), nullable=True))
    op.execute(
        """
        UPDATE residentes SET tipo_residente_id = CASE tipo_residente
            WHEN 'PROPIETARIO' THEN 1
            WHEN 'ARRENDATARIO' THEN 2
        END
        """
    )
    op.alter_column("residentes", "tipo_residente_id", nullable=False)
    op.create_foreign_key(
        "fk_residentes_tipo_residente",
        "residentes",
        "tipos_residente",
        ["tipo_residente_id"],
        ["id"],
    )
    op.drop_column("residentes", "tipo_residente")

    tipo_vehiculo_enum.drop(op.get_bind(), checkfirst=True)
    tipo_residente_enum.drop(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    tipo_vehiculo_enum.create(op.get_bind(), checkfirst=True)
    tipo_residente_enum.create(op.get_bind(), checkfirst=True)

    op.add_column("vehiculos", sa.Column("tipo_vehiculo", tipo_vehiculo_enum, nullable=True))
    op.execute(
        """
        UPDATE vehiculos SET tipo_vehiculo = tipos_vehiculo.codigo
        FROM tipos_vehiculo WHERE tipos_vehiculo.id = vehiculos.tipo_vehiculo_id
        """
    )
    op.alter_column("vehiculos", "tipo_vehiculo", nullable=False)
    op.drop_constraint("fk_vehiculos_tipo_vehiculo", "vehiculos", type_="foreignkey")
    op.drop_column("vehiculos", "tipo_vehiculo_id")

    op.add_column("residentes", sa.Column("tipo_residente", tipo_residente_enum, nullable=True))
    op.execute(
        """
        UPDATE residentes SET tipo_residente = tipos_residente.codigo
        FROM tipos_residente WHERE tipos_residente.id = residentes.tipo_residente_id
        """
    )
    op.alter_column("residentes", "tipo_residente", nullable=False)
    op.drop_constraint("fk_residentes_tipo_residente", "residentes", type_="foreignkey")
    op.drop_column("residentes", "tipo_residente_id")

    op.drop_table("tipos_residente")
    op.drop_table("tipos_vehiculo")