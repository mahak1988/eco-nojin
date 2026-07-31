"""merge parallel alembic branches

Revision ID: 20260729_0002
Revises: 0002_core_models, 20260729_0001
"""

from collections.abc import Sequence

revision: str = "20260729_0002"
down_revision: str | tuple | None = ("0002_core_models", "20260729_0001")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
