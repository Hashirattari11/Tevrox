from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ─── Ingredient schemas ──────────────────────────────────────────────────

class IngredientResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    name: str
    normalized_name: str
    description: Optional[str]
    reference_notes: Optional[str]
    category_function: Optional[str]


class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=300)
    description: Optional[str] = None
    reference_notes: Optional[str] = None
    category_function: Optional[str] = Field(
        default="other",
        comment="cleanser, toner, serum, moisturizer, sunscreen, mask, exfoliant, eye_care, treatment, other",
    )


class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    reference_notes: Optional[str] = None
    category_function: Optional[str] = Field(
        default=None,
        comment="cleanser, toner, serum, moisturizer, sunscreen, mask, exfoliant, eye_care, treatment, other",
    )


class IngredientAliasCreate(BaseModel):
    alias: str = Field(min_length=1, max_length=300)


class IngredientSearchResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    name: str
    normalized_name: str


# ─── Product Ingredient schemas ──────────────────────────────────────────

class ProductIngredientResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    product_id: UUID
    ingredient_id: UUID
    position: Optional[int]
    concentration: Optional[str]
    original_text: Optional[str]


# ─── Brand schema ───────────────────────────────────────────────────────

class BrandResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    name: str
    is_active: bool


# ─── Data Source schema ─────────────────────────────────────────────────

class DataSourceResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    name: str


# ─── Product schemas ─────────────────────────────────────────────────────

class ProductSummaryResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    name: str
    barcode: Optional[str]
    category: Optional[str]
    description: Optional[str]
    image_url: Optional[str]
    verification_status: str
    brand: Optional[BrandResponse]
    source: Optional[DataSourceResponse]
    ingredient_count: int = 0
    is_active: bool


class ProductDetailResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    name: str
    barcode: Optional[str]
    category: Optional[str]
    description: Optional[str]
    image_url: Optional[str]
    verification_status: str
    is_active: bool
    verified_by: Optional[str]
    verified_at: Optional[str]
    created_by: Optional[str]
    brand: Optional[BrandResponse]
    source: Optional[DataSourceResponse]
    ingredients: List[ProductIngredientResponse]


class ProductSearchFilters(BaseModel):
    q: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=300,
        json_schema_extra={"description": "Search term for name/brand"},
    )
    category: Optional[str] = Field(
        default=None,
        max_length=80,
        json_schema_extra={"description": "Category filter (cleanser, toner, serum, etc.)"},
    )
    brand: Optional[str] = Field(
        default=None,
        max_length=200,
        json_schema_extra={"description": "Brand name filter"},
    )
    verified_only: bool = Field(
        default=True, json_schema_extra={"description": "Show only verified products"}
    )
    skip: int = Field(default=0, ge=0, json_schema_extra={"description": "Number of records to skip"})
    limit: int = Field(default=50, ge=1, le=100, json_schema_extra={"description": "Maximum records to return"})


class ProductSubmissionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=300, description="Product name")
    category: str = Field(
        max_length=80,
        description="Category (cleanser, toner, serum, moisturizer, sunscreen, mask, exfoliant, eye_care, treatment, other)",
    )
    barcode: Optional[str] = Field(
        default=None,
        max_length=30,
        description="Barcode (8-14 digits, optional)",
    )
    ingredients_raw_text: str = Field(
        min_length=1,
        description="Raw ingredient list text from product label",
    )


class ProductSubmissionResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    name: str
    barcode: Optional[str]
    category: str
    verification_status: str
    message: str


class AdminProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=300)
    category: Optional[str] = Field(default=None, max_length=80)
    verification_status: str = Field(
        default="verified",
        description="'verified' or 'rejected'",
    )
    reason: Optional[str] = Field(default=None, max_length=500)


class AdminAuditLogCreate(BaseModel):
    action: str = Field(min_length=1, max_length=160)
    entity_type: str = Field(max_length=120)
    entity_id: UUID
    before_summary: Optional[str] = Field(default=None, max_length=500)
    after_summary: Optional[str] = Field(default=None, max_length=500)