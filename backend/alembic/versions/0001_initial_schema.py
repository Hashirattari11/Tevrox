"""Initial schema for users, product catalog, routines, and nutrition."""

import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

# Portable JSON: JSONB on PostgreSQL, generic JSON elsewhere (e.g. SQLite checks).
PortableJSONB = sa.JSON().with_variant(JSONB(), "postgresql")

ENUMS = ("user_role", "verification_status", "routine_type")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid, primary_key=True, default=uuid.uuid4),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("user", "admin", name="user_role"), nullable=False),
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
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Uuid, primary_key=True, default=uuid.uuid4),
        sa.Column(
            "user_id",
            sa.Uuid,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("display_name", sa.String(120)),
        sa.Column("skin_type", sa.String(80)),
        sa.Column("dietary_preferences", PortableJSONB),
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
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_user_profiles_user_id", "user_profiles", ["user_id"])

    op.create_table(
        "data_sources",
        sa.Column("id", sa.Uuid, primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("url", sa.String(2048)),
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
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "brands",
        sa.Column("id", sa.Uuid, primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(200), nullable=False),
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
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_brands_name", "brands", ["name"], unique=True)

    op.create_table(
        "products",
        sa.Column("id", sa.Uuid, primary_key=True, default=uuid.uuid4),
        sa.Column(
            "brand_id",
            sa.Uuid,
            sa.ForeignKey("brands.id", ondelete="SET NULL"),
            index=True,
        ),
        sa.Column(
            "source_id",
            sa.Uuid,
            sa.ForeignKey("data_sources.id", ondelete="SET NULL"),
            index=True,
        ),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("barcode", sa.String(64), unique=True),
        sa.Column("description", sa.Text()),
        sa.Column(
            "verification_status",
            sa.Enum("unverified", "verified", "rejected", name="verification_status"),
            nullable=False,
        ),
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
    op.create_index("ix_products_barcode", "products", ["barcode"], unique=True)
    op.create_index("ix_products_verification_status", "products", ["verification_status"])
    op.create_index("ix_products_name", "products", ["name"])

    op.create_table(
        "ingredients",
        sa.Column("id", sa.Uuid, primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("normalized_name", sa.String(300), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("reference_notes", sa.Text()),
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
        sa.UniqueConstraint("normalized_name"),
    )
    op.create_index(
        "ix_ingredients_normalized_name", "ingredients", ["normalized_name"], unique=True
    )

    op.create_table(
        "product_ingredients",
        sa.Column("id", sa.Uuid, primary_key=True, default=uuid.uuid4),
        sa.Column(
            "product_id",
            sa.Uuid,
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "ingredient_id",
            sa.Uuid,
            sa.ForeignKey("ingredients.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("position", sa.Integer()),
        sa.Column("concentration", sa.String(80)),
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
        sa.UniqueConstraint("product_id", "ingredient_id"),
    )

    op.create_table(
        "analyses",
        sa.Column("id", sa.Uuid, primary_key=True, default=uuid.uuid4),
        sa.Column(
            "user_id",
            sa.Uuid,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "product_id",
            sa.Uuid,
            sa.ForeignKey("products.id", ondelete="SET NULL"),
            index=True,
        ),
        sa.Column("structured_result", PortableJSONB, nullable=False),
        sa.Column("model_used", sa.String(120), nullable=False),
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

    op.create_table(
        "routines",
        sa.Column("id", sa.Uuid, primary_key=True, default=uuid.uuid4),
        sa.Column(
            "user_id",
            sa.Uuid,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("type", sa.Enum("morning", "evening", name="routine_type"), nullable=False),
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

    op.create_table(
        "routine_items",
        sa.Column("id", sa.Uuid, primary_key=True, default=uuid.uuid4),
        sa.Column(
            "routine_id",
            sa.Uuid,
            sa.ForeignKey("routines.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "product_id",
            sa.Uuid,
            sa.ForeignKey("products.id", ondelete="SET NULL"),
            index=True,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text()),
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
        sa.UniqueConstraint("routine_id", "position"),
    )

    op.create_table(
        "nutrition_entries",
        sa.Column("id", sa.Uuid, primary_key=True, default=uuid.uuid4),
        sa.Column(
            "user_id",
            sa.Uuid,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "product_id",
            sa.Uuid,
            sa.ForeignKey("products.id", ondelete="SET NULL"),
            index=True,
        ),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("quantity", sa.String(80)),
        sa.Column("nutrients", PortableJSONB),
        sa.Column("notes", sa.Text()),
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

    op.create_table(
        "admin_audit_logs",
        sa.Column("id", sa.Uuid, primary_key=True, default=uuid.uuid4),
        sa.Column(
            "admin_user_id",
            sa.Uuid,
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            index=True,
        ),
        sa.Column("action", sa.String(160), nullable=False),
        sa.Column("entity_type", sa.String(120), nullable=False),
        sa.Column("entity_id", sa.Uuid),
        sa.Column("metadata", sa.JSON()),
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



def downgrade() -> None:
    for table in (
        "admin_audit_logs",
        "nutrition_entries",
        "routine_items",
        "routines",
        "analyses",
        "product_ingredients",
        "ingredients",
        "products",
        "brands",
        "data_sources",
        "user_profiles",
        "users",
    ):
        op.drop_table(table)
    if op.get_bind().dialect.name == "postgresql":
        for enum_name in ENUMS:
            op.execute(sa.text(f"DROP TYPE IF EXISTS {enum_name}"))
