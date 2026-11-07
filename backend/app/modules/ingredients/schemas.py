from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

FUNCTIONAL_CATEGORIES = {
    "humectant",
    "emollient",
    "antioxidant",
    "surfactant",
    "preservative",
    "active",
    "uv_filter",
    "fragrance",
    "solvent",
    "buffer",
    "other",
}


class IngredientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    normalized_name: str
    description: str | None = None
    reference_notes: str | None = None
    category_function: str | None = None
    is_reviewed: bool = False
    is_active: bool = True


class IngredientSearchItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    normalized_name: str


class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=300)
    description: str | None = None
    reference_notes: str | None = None
    category_function: str = Field(default="other", max_length=100)
    is_reviewed: bool = True

    @field_validator("category_function")
    @classmethod
    def validate_category(cls, value: str) -> str:
        if value not in FUNCTIONAL_CATEGORIES:
            raise ValueError(f"Unsupported ingredient function: {value}")
        return value


class IngredientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = None
    reference_notes: str | None = None
    category_function: str | None = Field(default=None, max_length=100)
    is_reviewed: bool | None = None
    is_active: bool | None = None

    @field_validator("category_function")
    @classmethod
    def validate_category(cls, value: str | None) -> str | None:
        if value is not None and value not in FUNCTIONAL_CATEGORIES:
            raise ValueError(f"Unsupported ingredient function: {value}")
        return value


class IngredientAliasCreate(BaseModel):
    ingredient_id: UUID
    alias: str = Field(min_length=1, max_length=300)


class IngredientMergeRequest(BaseModel):
    source_id: UUID
    target_id: UUID


class IngredientMergeResponse(BaseModel):
    message: str
    source_id: UUID
    target_id: UUID
    moved_product_ingredients: int
    dropped_duplicate_links: int
    moved_aliases: int


class IngredientAdminListResponse(BaseModel):
    items: list[IngredientResponse]
    total: int
    unreviewed_only: bool
