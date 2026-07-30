"""Add admin panel models (idempotent for SQLite / create_all coexistence)

Revision ID: 0001_admin_models
Revises: None
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_admin_models"
down_revision = None
branch_labels = None
depends_on = None


def _tables() -> set[str]:
    bind = op.get_bind()
    return set(sa.inspect(bind).get_table_names())


def _has_index(table: str, name: str) -> bool:
    bind = op.get_bind()
    try:
        return any(ix["name"] == name for ix in sa.inspect(bind).get_indexes(table))
    except Exception:
        return False


def upgrade() -> None:
    existing = _tables()

    if "admin_settings" not in existing:
        op.create_table(
            "admin_settings",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("key", sa.String(length=128), nullable=False, unique=True),
            sa.Column("value", sa.Text(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )

    if "audit_logs" not in existing:
        op.create_table(
            "audit_logs",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("actor_id", sa.Integer(), nullable=True),
            sa.Column("actor_email", sa.String(length=255), nullable=True),
            sa.Column("event_type", sa.String(length=128), nullable=False),
            sa.Column("event_data", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    if not _has_index("audit_logs", "ix_audit_logs_event_type"):
        try:
            op.create_index("ix_audit_logs_event_type", "audit_logs", ["event_type"])
        except Exception:
            pass

    if "system_reports" not in existing:
        op.create_table(
            "system_reports",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("report_name", sa.String(length=255), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'pending'")),
            sa.Column("report_data", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        )
    if not _has_index("system_reports", "ix_system_reports_report_name"):
        try:
            op.create_index("ix_system_reports_report_name", "system_reports", ["report_name"])
        except Exception:
            pass


def downgrade() -> None:
    try:
        op.drop_index("ix_system_reports_report_name", table_name="system_reports")
    except Exception:
        pass
    try:
        op.drop_table("system_reports")
    except Exception:
        pass
    try:
        op.drop_index("ix_audit_logs_event_type", table_name="audit_logs")
    except Exception:
        pass
    try:
        op.drop_table("audit_logs")
    except Exception:
        pass
    try:
        op.drop_table("admin_settings")
    except Exception:
        pass
