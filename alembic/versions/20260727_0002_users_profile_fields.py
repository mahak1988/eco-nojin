"""users phone organization role

Revision ID: 20260727_0002
Revises: 20260727_0001
Create Date: 2026-07-27
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260727_0002"
down_revision: Union[str, None] = "20260727_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "users" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("users")}
    if "phone" not in cols:
        op.add_column("users", sa.Column("phone", sa.String(40), nullable=True))
    if "organization" not in cols:
        op.add_column("users", sa.Column("organization", sa.String(255), nullable=True))
    if "role" not in cols:
        op.add_column(
            "users",
            sa.Column("role", sa.String(40), nullable=False, server_default="farmer"),
        )


def downgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "users" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("users")}
    for name in ("role", "organization", "phone"):
        if name in cols:
            op.drop_column("users", name)
