import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    false,
    func,
    true,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

# Portable JSON: JSONB on PostgreSQL, generic JSON elsewhere (used by tests on SQLite).
PortableJSONB = JSON().with_variant(JSONB(), "postgresql")


class SkinType(enum.StrEnum):
    dry = "dry"
    oily = "oily"
    combination = "combination"
    normal = "normal"
    sensitive = "sensitive"


SKIN_TYPE_VALUES = tuple(skin_type.value for skin_type in SkinType)
SKIN_CONCERNS: tuple[str, ...] = (
    "acne",
    "dryness",
    "redness",
    "pigmentation",
    "aging",
    "dullness",
    "large pores",
    "sensitivity",
)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class UserRole(enum.StrEnum):
    user = "user"
    admin = "admin"


class VerificationStatus(enum.StrEnum):
    unverified = "unverified"
    verified = "verified"
    rejected = "rejected"


class RoutineType(enum.StrEnum):
    morning = "morning"
    evening = "evening"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), default=UserRole.user)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, server_default="true")
    is_email_verified: Mapped[bool] = mapped_column(
        default=False, nullable=False, server_default="false"
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class UserProfile(TimestampMixin, Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    display_name: Mapped[str | None] = mapped_column(String(120))
    skin_type: Mapped[str | None] = mapped_column(String(80))
    dietary_preferences: Mapped[dict[str, Any] | None] = mapped_column(PortableJSONB)
    full_name: Mapped[str | None] = mapped_column(String(160))
    skin_concerns: Mapped[list[str]] = mapped_column(PortableJSONB, default=list, nullable=False)
    preferences: Mapped[dict[str, Any]] = mapped_column(PortableJSONB, default=dict, nullable=False)
    onboarding_completed: Mapped[bool] = mapped_column(
        default=False, nullable=False, server_default="false"
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    family_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replaced_by: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    user_agent: Mapped[str | None] = mapped_column(String(512))
    ip_address: Mapped[str | None] = mapped_column(String(64))


class DataSource(TimestampMixin, Base):
    __tablename__ = "data_sources"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(160), unique=True)
    url: Mapped[str | None] = mapped_column(String(2048))

    products = relationship("Product", back_populates="source")


class Brand(TimestampMixin, Base):
    __tablename__ = "brands"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)

    products = relationship("Product", back_populates="brand")


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (Index("ix_products_name", "name"), Index("ix_products_barcode", "barcode"))

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    brand_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("brands.id", ondelete="SET NULL"), index=True
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("data_sources.id", ondelete="SET NULL"), index=True
    )
    name: Mapped[str] = mapped_column(String(300))
    barcode: Mapped[str | None] = mapped_column(String(64), unique=True, index=True, nullable=True)
    category: Mapped[str | None] = mapped_column(
        String(80),
        server_default="other",
        comment="cleanser, toner, serum, moisturizer, sunscreen, mask, exfoliant, eye_care, treatment, other",
    )
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))
    ingredients_raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status"),
        default=VerificationStatus.unverified,
        index=True,
    )
    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, server_default="true")

    brand = relationship("Brand", back_populates="products")
    source = relationship("DataSource", back_populates="products")
    product_ingredients = relationship(
        "ProductIngredient", back_populates="product", cascade="all, delete-orphan"
    )


class Ingredient(TimestampMixin, Base):
    __tablename__ = "ingredients"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(300))
    normalized_name: Mapped[str] = mapped_column(String(300), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    reference_notes: Mapped[str | None] = mapped_column(Text)
    category_function: Mapped[str | None] = mapped_column(
        String(100),
        server_default="other",
        comment="cleanser, toner, serum, moisturizer, sunscreen, mask, exfoliant, eye_care, treatment, other",
    )

    product_ingredients = relationship(
        "ProductIngredient", back_populates="ingredient", cascade="all, delete-orphan"
    )


class IngredientAlias(Base):
    __tablename__ = "ingredient_aliases"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("ingredients.id", ondelete="CASCADE"), index=True
    )
    alias_normalized: Mapped[str] = mapped_column(String(300), unique=True, index=True)


class ProductIngredient(TimestampMixin, Base):
    __tablename__ = "product_ingredients"
    __table_args__ = (UniqueConstraint("product_id", "ingredient_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("ingredients.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int | None] = mapped_column(Integer)
    concentration: Mapped[str | None] = mapped_column(String(80))
    original_text: Mapped[str | None] = mapped_column(String(500))

    product = relationship("Product", back_populates="product_ingredients")
    ingredient = relationship("Ingredient", back_populates="product_ingredients")


class Analysis(TimestampMixin, Base):
    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("products.id", ondelete="SET NULL"), index=True
    )
    structured_result: Mapped[dict[str, Any]] = mapped_column(PortableJSONB)
    model_used: Mapped[str] = mapped_column(String(120))


class Routine(TimestampMixin, Base):
    __tablename__ = "routines"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(160))
    type: Mapped[RoutineType] = mapped_column(Enum(RoutineType, name="routine_type"))


class RoutineItem(TimestampMixin, Base):
    __tablename__ = "routine_items"
    __table_args__ = (UniqueConstraint("routine_id", "position"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    routine_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("routines.id", ondelete="CASCADE"), index=True
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("products.id", ondelete="SET NULL"), index=True
    )
    position: Mapped[int] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)


class NutritionEntry(TimestampMixin, Base):
    __tablename__ = "nutrition_entries"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("products.id", ondelete="SET NULL"), index=True
    )
    consumed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    quantity: Mapped[str | None] = mapped_column(String(80))
    nutrients: Mapped[dict[str, Any] | None] = mapped_column(PortableJSONB)
    notes: Mapped[str | None] = mapped_column(Text)


class AdminAuditLog(TimestampMixin, Base):
    __tablename__ = "admin_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    admin_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    action: Mapped[str] = mapped_column(String(160))
    entity_type: Mapped[str] = mapped_column(String(120))
    entity_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    before_summary: Mapped[str | None] = mapped_column(String(500))
    after_summary: Mapped[str | None] = mapped_column(String(500))
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)
