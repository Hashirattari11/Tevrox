from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

SKIN_TYPES = {"dry", "oily", "combination", "normal", "sensitive"}
SKIN_CONCERNS = {
    "acne",
    "dryness",
    "redness",
    "pigmentation",
    "aging",
    "dullness",
    "large pores",
    "sensitivity",
}


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=160)
    skin_type: str | None = None
    skin_concerns: list[str] = Field(default_factory=list, max_length=8)
    preferences: dict[str, Any] = Field(default_factory=dict)
    onboarding_completed: bool = False

    @field_validator("skin_type")
    @classmethod
    def validate_skin_type(cls, value: str | None) -> str | None:
        if value is not None and value not in SKIN_TYPES:
            raise ValueError("Unsupported skin type")
        return value

    @field_validator("skin_concerns")
    @classmethod
    def validate_concerns(cls, values: list[str]) -> list[str]:
        if not set(values) <= SKIN_CONCERNS:
            raise ValueError("Unsupported skin concern")
        return values


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    full_name: str | None
    skin_type: str | None
    skin_concerns: list[str]
    preferences: dict[str, Any]
    onboarding_completed: bool
