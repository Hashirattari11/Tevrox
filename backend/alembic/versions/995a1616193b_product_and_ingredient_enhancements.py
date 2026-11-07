"""product and ingredient enhancements

Revision ID: 995a1616193b
Revises: 0002_auth_profiles
Create Date: 2026-11-04 20:55:20.074200
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = '995a1616193b'
down_revision: str | None = '0002_auth_profiles'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add new columns to products table
    op.add_column(
        "products",
        sa.Column(
            "category",
            sa.String(80),
            server_default="other",
            comment=(
                "cleanser, toner, serum, moisturizer, sunscreen, mask, exfoliant, eye_care, "
                "treatment, other"
            ),
        ),
    )
    op.add_column(
        "products",
        sa.Column("image_url", sa.String(500), nullable=True),
    )
    op.add_column(
        "products",
        sa.Column("ingredients_raw_text", sa.Text(), nullable=True),
    )
    op.add_column(
        "products",
        sa.Column("external_id", sa.String(100), nullable=True),
    )
    op.add_column(
        "products",
        sa.Column("verified_by", sa.Uuid, nullable=True),
    )
    op.add_column(
        "products",
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "products",
        sa.Column("created_by", sa.Uuid, nullable=True),
    )
    op.add_column(
        "products",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )
    # Update index to include barcode
    op.drop_index("ix_products_name", table_name="products")
    op.create_index("ix_products_name", "products", ["name"], unique=False)
    op.create_index(
        "ix_products_barcode", "products", ["barcode"], unique=False, if_not_exists=True
    )

    # Add new columns to ingredients table
    op.add_column(
        "ingredients",
        sa.Column(
            "category_function",
            sa.String(100),
            server_default="other",
            comment=(
                "cleanser, toner, serum, moisturizer, sunscreen, mask, exfoliant, eye_care, "
                "treatment, other"
            ),
        ),
    )

    # Create ingredient_aliases table
    op.create_table(
        "ingredient_aliases",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column(
            "ingredient_id",
            sa.Uuid,
            sa.ForeignKey("ingredients.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("alias_normalized", sa.String(300), unique=True, nullable=False),
    )
    op.create_index(
        "ix_ingredient_aliases_ingredient_id", "ingredient_aliases", ["ingredient_id"]
    )

    # Update product_ingredients table
    op.add_column(
        "product_ingredients",
        sa.Column("original_text", sa.String(500), nullable=True),
    )

    # data_sources seed. The id column is a UUID, so generate real UUIDs rather
    # than integers (PostgreSQL rejects integer values for UUID columns).
    import uuid

    op.bulk_insert(
        sa.table(
            "data_sources",
            sa.Column("id", sa.Uuid),
            sa.Column("name", sa.String(160), nullable=False),
        ),
        [
            {"id": uuid.uuid4(), "name": "internal_admin"},
            {"id": uuid.uuid4(), "name": "open_beauty_facts"},
            {"id": uuid.uuid4(), "name": "user_submitted"},
        ],
    )


def downgrade() -> None:
    # Remove ingredient_aliases table and index
    op.drop_index("ix_ingredient_aliases_ingredient_id", table_name="ingredient_aliases")
    op.drop_table("ingredient_aliases")

    # Remove original_text from product_ingredients
    op.drop_column("product_ingredients", "original_text")

    # Remove columns from ingredients
    op.drop_column("ingredients", "category_function")

    # Remove columns from products
    op.drop_column("products", "is_active")
    op.drop_column("products", "created_by")
    op.drop_column("products", "verified_at")
    op.drop_column("products", "verified_by")
    op.drop_column("products", "external_id")
    op.drop_column("products", "ingredients_raw_text")
    op.drop_column("products", "image_url")
    op.drop_column("products", "category")

    # Drop indexes
    op.drop_index("ix_products_barcode", table_name="products", if_exists=True)
    op.drop_index("ix_products_name", table_name="products")

    # Remove data_sources seed rows
    op.execute(
        sa.text(
            "DELETE FROM data_sources "
            "WHERE name IN ('internal_admin', 'open_beauty_facts', 'user_submitted')"
        )
    )