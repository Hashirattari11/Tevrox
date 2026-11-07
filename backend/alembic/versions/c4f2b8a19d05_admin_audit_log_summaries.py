"""admin audit log summaries

Revision ID: c4f2b8a19d05
Revises: 995a1616193b
Create Date: 2026-11-05 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = 'c4f2b8a19d05'
down_revision: str | None = '995a1616193b'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "admin_audit_logs",
        sa.Column("before_summary", sa.String(500), nullable=True),
    )
    op.add_column(
        "admin_audit_logs",
        sa.Column("after_summary", sa.String(500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("admin_audit_logs", "after_summary")
    op.drop_column("admin_audit_logs", "before_summary")
