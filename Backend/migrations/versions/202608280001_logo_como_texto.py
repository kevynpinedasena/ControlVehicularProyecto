"""Amplía logo_url a texto sin límite (para guardar el logo como data URI en vez de ruta de disco).

Revision ID: 202608280001
Revises: 202608270001
Create Date: 2026-08-28

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202608280001"
down_revision: Union[str, None] = "202608270001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "unidades_negocio",
        "logo_url",
        existing_type=sa.String(500),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "unidades_negocio",
        "logo_url",
        existing_type=sa.Text(),
        type_=sa.String(500),
        existing_nullable=True,
    )
