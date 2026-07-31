"""RBAC tables: roles, permissions, role_permissions, user_roles.

Revision ID: 20260727_0002
Revises: 20260727_0001
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260727_0002"
down_revision: str | None = "20260727_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    existing = set(insp.get_table_names())

    if "roles" not in existing:
        op.create_table(
            "roles",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.String(length=64), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
        )
        op.create_index("ix_roles_name", "roles", ["name"])

    if "permissions" not in existing:
        op.create_table(
            "permissions",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("code", sa.String(length=128), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("code"),
        )
        op.create_index("ix_permissions_code", "permissions", ["code"])

    if "role_permissions" not in existing:
        op.create_table(
            "role_permissions",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("role_id", sa.Integer(), nullable=False),
            sa.Column("permission_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
        )

    if "user_roles" not in existing:
        op.create_table(
            "user_roles",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("role_id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "role_id", name="uq_user_role"),
        )
        op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"])


def downgrade() -> None:
    for idx, table in (
        ("ix_user_roles_user_id", "user_roles"),
        (None, "user_roles"),
        (None, "role_permissions"),
        ("ix_permissions_code", "permissions"),
        (None, "permissions"),
        ("ix_roles_name", "roles"),
        (None, "roles"),
    ):
        try:
            if idx:
                op.drop_index(idx, table_name=table)
            else:
                op.drop_table(table)
        except Exception:
            pass
