"""Phase 3 catalogue hardening: ingredient review flags and search indexes.

Revision ID: 0003_phase3_catalog
Revises: c4f2b8a19d05
Create Date: 2026-11-07 09:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_phase3_catalog"
down_revision: str | None = "c4f2b8a19d05"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ingredients",
        sa.Column(
            "is_reviewed", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.add_column(
        "ingredients",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_ingredients_is_reviewed", "ingredients", ["is_reviewed"])
    op.create_index("ix_products_is_active", "products", ["is_active"])
    op.create_index("ix_products_category", "products", ["category"])

    # PostgreSQL: trigram indexes make leading-wildcard ILIKE searches usable.
    # SQLite (development/tests) falls back to a normal ILIKE scan; the same
    # query code is used on both backends.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        op.execute(
            "CREATE INDEX IF NOT EXISTS ix_products_name_trgm "
            "ON products USING gin (name gin_trgm_ops)"
        )
        op.execute(
            "CREATE INDEX IF NOT EXISTS ix_ingredients_normalized_name_trgm "
            "ON ingredients USING gin (normalized_name gin_trgm_ops)"
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP INDEX IF EXISTS ix_ingredients_normalized_name_trgm")
        op.execute("DROP INDEX IF EXISTS ix_products_name_trgm")

    op.drop_index("ix_products_category", table_name="products")
    op.drop_index("ix_products_is_active", table_name="products")
    op.drop_index("ix_ingredients_is_reviewed", table_name="ingredients")
    op.drop_column("ingredients", "is_active")
    op.drop_column("ingredients", "is_reviewed")
