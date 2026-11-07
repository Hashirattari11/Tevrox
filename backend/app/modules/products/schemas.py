from __future__ import annotations

import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

PRODUCT_CATEGORIES = (
    "cleanser",
    "toner",
    "serum",
    "moisturizer",
    "sunscreen",
    "mask",
    "exfoliant",
    "eye_care",
    "treatment",
    "other",
)
VERIFICATION_STATUSES = ("unverified", "verified", "rejected")


def normalize_category(value: str | None) -> str:
    category = (value or "other").strip().lower().replace(" ", "_").replace("-", "_")
    if category not in PRODUCT_CATEGORIES:
        raise ValueError(f"Unsupported product category: {value}")
    return category


def validate_barcode(value: str | None) -> str | None:
    if value is None:
        return None
    digits = re.sub(r"\D", "", value)
    if not digits:
        return None
    if not (8 <= len(digits) <= 14):
        raise ValueError("Barcode must contain 8 to 14 digits")
    return digits


class BrandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class ProductIngredientDetail(BaseModel):
    id: UUID
    product_id: UUID
    ingredient_id: UUID
    name: str
    normalized_name: str
    position: int | None = None
    original_text: str | None = None
    concentration: str | None = None
    category_function: str | None = None
    description: str | None = None


class ProductSummary(BaseModel):
    id: UUID
    name: str
    barcode: str | None = None
    category: str | None = None
    description: str | None = None
    image_url: str | None = None
    verification_status: str
    brand: BrandResponse | None = None
    source: SourceResponse | None = None
    ingredient_count: int = 0
    is_active: bool = True


class ProductDetail(ProductSummary):
    verified_by: UUID | None = None
    verified_at: datetime | None = None
    created_by: UUID | None = None
    ingredients_raw_text: str | None = None
    ingredients: list[ProductIngredientDetail] = Field(default_factory=list)


class ProductListResponse(BaseModel):
    items: list[ProductSummary]
    total: int
    limit: int
    next_cursor: str | None = None
    verified_only: bool = True


class CategoryCount(BaseModel):
    category: str
    count: int


class CategoriesResponse(BaseModel):
    categories: list[CategoryCount]


class ProductSubmissionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=300)
    brand_name: str | None = Field(default=None, max_length=200)
    category: str = Field(default="other", max_length=80)
    barcode: str | None = Field(default=None, max_length=30)
    ingredients_raw_text: str = Field(min_length=1, max_length=100_000)

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        return normalize_category(value)

    @field_validator("barcode")
    @classmethod
    def validate_barcode(cls, value: str | None) -> str | None:
        return validate_barcode(value)

    @field_validator("name", "ingredients_raw_text")
    @classmethod
    def strip_required(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Value cannot be blank")
        return stripped


class ProductSubmissionResponse(BaseModel):
    id: UUID
    name: str
    barcode: str | None = None
    category: str
    verification_status: str
    message: str


class AdminProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=300)
    brand_name: str | None = Field(default=None, max_length=200)
    category: str = Field(default="other", max_length=80)
    barcode: str | None = Field(default=None, max_length=30)
    description: str | None = Field(default=None, max_length=5_000)
    image_url: str | None = Field(default=None, max_length=500)
    ingredients_raw_text: str | None = Field(default=None, max_length=100_000)
    verification_status: str = "unverified"

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        return normalize_category(value)

    @field_validator("barcode")
    @classmethod
    def validate_barcode(cls, value: str | None) -> str | None:
        return validate_barcode(value)

    @field_validator("verification_status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in VERIFICATION_STATUSES:
            raise ValueError("Unsupported verification status")
        return value


class AdminProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=300)
    brand_name: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=80)
    barcode: str | None = Field(default=None, max_length=30)
    description: str | None = Field(default=None, max_length=5_000)
    image_url: str | None = Field(default=None, max_length=500)
    ingredients_raw_text: str | None = Field(default=None, max_length=100_000)

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str | None) -> str | None:
        return normalize_category(value) if value is not None else None

    @field_validator("barcode")
    @classmethod
    def validate_barcode(cls, value: str | None) -> str | None:
        return validate_barcode(value)


class ProductVerificationRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class AdminActionResponse(BaseModel):
    message: str
    product_id: UUID
    verification_status: str


class ReviewQueueResponse(BaseModel):
    items: list[ProductSummary]
    total: int
    source: str | None = None
