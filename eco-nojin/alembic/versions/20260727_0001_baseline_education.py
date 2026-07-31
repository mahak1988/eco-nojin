"""Baseline: education core tables (courses, lessons, enrollments).

Revision ID: 20260727_0001
Revises:
Create Date: 2026-07-27

Idempotent: skips create if tables already exist (local SQLite via create_all).
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260727_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = set(insp.get_table_names())

    if "courses" not in tables:
        op.create_table(
            "courses",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("category", sa.String(length=100), nullable=False),
            sa.Column("level", sa.String(length=50), nullable=False, server_default="beginner"),
            sa.Column("duration_hours", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("instructor", sa.String(length=255), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_courses_title", "courses", ["title"])
        op.create_index("ix_courses_category", "courses", ["category"])

    if "lessons" not in tables:
        op.create_table(
            "lessons",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("course_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("content", sa.Text(), nullable=True),
            sa.Column("video_url", sa.String(length=500), nullable=True),
            sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
            sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_lessons_course_id", "lessons", ["course_id"])

    if "enrollments" not in tables:
        op.create_table(
            "enrollments",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("course_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("enrolled_at", sa.DateTime(), nullable=False),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_enrollments_course_id", "enrollments", ["course_id"])
        op.create_index("ix_enrollments_user_id", "enrollments", ["user_id"])


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = set(insp.get_table_names())
    if "enrollments" in tables:
        op.drop_table("enrollments")
    if "lessons" in tables:
        op.drop_table("lessons")
    if "courses" in tables:
        op.drop_table("courses")
