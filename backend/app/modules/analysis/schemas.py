"""Pydantic schemas for the AI ingredient analysis module (Phase 4).

Strict validation of AI output and API request/response bodies.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class KeyIngredient(BaseModel):
    """A single ingredient in the analysis result."""

    ingredient_id: UUID
    name: str = Field(max_length=300)
    role: str = Field(max_length=100)
    explanation: str = Field(max_length=1000)
    caution_level: str = Field(
        default="info",
        description="info | note | caution",
    )

    @field_validator("caution_level")
    @classmethod
    def validate_caution_level(cls, value: str) -> str:
        if value not in {"info", "note", "caution"}:
            raise ValueError("caution_level must be info, note, or caution")
        return value


class AnalysisResult(BaseModel):
    """Strict schema for AI-generated ingredient analysis output."""

    model_config = ConfigDict(str_strip_whitespace=True)

    summary: str = Field(max_length=600)
    suitability_overview: str = Field(max_length=2000)
    key_ingredients: list[KeyIngredient] = Field(default_factory=list)
    cautions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    confidence: str = Field(default="medium")
    confidence_reason: str = Field(max_length=1000, default="")

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, value: str) -> str:
        if value not in {"low", "medium", "high"}:
            raise ValueError("confidence must be low, medium, or high")
        return value

    @field_validator("key_ingredients")
    @classmethod
    def validate_not_empty(cls, value: list[KeyIngredient]) -> list[KeyIngredient]:
        if not value:
            raise ValueError("key_ingredients must not be empty")
        return value


# Standard limitation entries merged into every report by the backend,
# regardless of model output.
STANDARD_LIMITATIONS: list[str] = [
    "Tevrox provides educational information about cosmetic ingredients. "
    "It is not medical advice and does not diagnose or treat any condition. "
    "If you have skin concerns or a reaction, talk to a qualified professional.",
    "This analysis is based on ingredient lists, not on product testing or "
    "clinical data.",
    "Individual skin reactions vary; results are educational, not personalised "
    "medical guidance.",
]

# Banned medical-claim phrases (case-insensitive). If any appear in model
# output, validation fails and the report is retried or falls back.
BANNED_PHRASES: list[str] = [
    "cure",
    "cures",
    "treated",
    "treats",
    "treatment",
    "heal",
    "heals",
    "healing",
    "diagnose",
    "diagnoses",
    "diagnosis",
    "prescribe",
    "prescribes",
    "prescription",
    "clinically proven",
    "clinically-proven",
    "guaranteed",
    "guarantee",
    "acne",
    "eczema",
    "psoriasis",
    "rosacea",
    "cancer",
    "tumor",
    "tumour",
]


class AnalysisCreate(BaseModel):
    """Request to create a new analysis."""

    product_id: UUID


class AnalysisResponse(BaseModel):
    """Response returned by analysis endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID | None = None
    status: str
    model_used: str
    prompt_version: str | None = None
    rules_version: str | None = None
    latency_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    error_code: str | None = None
    created_at: str
    result: AnalysisResult
