from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, field_validator


class IngredientResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    name: str
    normalized_name: str
    description: Optional[str]
    reference_notes: Optional[str]
    category_function: Optional[str]
    is_active: bool


class IngredientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=300, json_schema_extra={"comment": "trim, lowercase, collapse whitespace, remove trailing punctuation, strip bracketed percentages, unify unicode, handle 'Aqua / Water' style slashes"})
    description: Optional[str] = None
    reference_notes: Optional[str] = None
    category_function: Optional[str] = Field(
        default="other",
        json_schema_extra={"comment": "cleanser, toner, serum, moisturizer, sunscreen, mask, exfoliant, eye_care, treatment, other"},
    )

    @field_validator("name")
    @classmethod
    def normalize_ingredient_name(cls, value: str) -> str:
        import re

        value = value.strip().lower()
        # Remove bracketed percentages like (10%) or [5%]
        value = re.sub(r"\(.*?\)", "", value)
        value = re.sub(r"\[.*?\]", "", value)
        # Collapse whitespace
        value = re.sub(r"\s+", " ", value)
        return value.strip()


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

    @field_validator("alias")
    @classmethod
    def normalize_alias(cls, value: str) -> str:
        import re
        value = value.strip().lower()
        value = re.sub(r"\s+", " ", value)
        return value.strip()


class IngredientSearchResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    name: str
    normalized_name: str


class ProductIngredientResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    product_id: UUID
    ingredient_id: UUID
    position: Optional[int]
    concentration: Optional[str]
    original_text: Optional[str]