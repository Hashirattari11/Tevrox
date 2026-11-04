from functools import lru_cache

from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings; secrets are never assigned defaults."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://localhost/tevrox"
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "tevrox"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    jwt_secret: str = ""
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    jwt_algorithm: str = "HS256"
    allowed_origins: str = "http://localhost:3000,http://localhost:8081"
    environment: str = "development"
    ai_provider_api_key: str = ""
    product_api_key: str = ""
    app_name: str = "Tevrox API"
    app_version: str = "0.1.0"

    @model_validator(mode="after")
    def validate_jwt_secret(self) -> "Settings":
        if self.environment != "test" and len(self.jwt_secret) < 32:
            raise ValueError("JWT_SECRET must contain at least 32 characters")
        return self

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
