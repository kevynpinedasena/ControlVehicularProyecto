"""Agrega telefono_1 y telefono_2 a residentes.

Revision ID: 202608250001
Revises: 202608240001
Create Date: 2026-08-25

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202608250001"
down_revision: Union[str, None] = "202608240001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("residentes", sa.Column("telefono_1", sa.String(30), nullable=True))
    op.add_column("residentes", sa.Column("telefono_2", sa.String(30), nullable=True))


def downgrade() -> None:
    op.drop_column("residentes", "telefono_2")
    op.drop_column("residentes", "telefono_1")
