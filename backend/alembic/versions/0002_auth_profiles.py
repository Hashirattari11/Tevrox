"""Authentication and profile lifecycle."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0002_auth_profiles"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users", sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False)
    )
    op.add_column(
        "users",
        sa.Column("is_email_verified", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True)))
    op.add_column("user_profiles", sa.Column("full_name", sa.String(160)))
    op.add_column(
        "user_profiles",
        sa.Column("skin_concerns", postgresql.JSONB(), server_default="[]", nullable=False),
    )
    op.add_column(
        "user_profiles",
        sa.Column("preferences", postgresql.JSONB(), server_default="{}", nullable=False),
    )
    op.add_column(
        "user_profiles",
        sa.Column("onboarding_completed", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("family_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("replaced_by", postgresql.UUID(as_uuid=True)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("user_agent", sa.String(512)),
        sa.Column("ip_address", sa.String(64)),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_family_id", "refresh_tokens", ["family_id"])


def downgrade() -> None:
    op.drop_index("ix_refresh_tokens_family_id", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    for column in ("onboarding_completed", "preferences", "skin_concerns", "full_name"):
        op.drop_column("user_profiles", column)
    for column in ("last_login_at", "is_email_verified", "is_active"):
        op.drop_column("users", column)
