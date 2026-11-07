"""AI provider layer for Tevrox ingredient analysis.

Provider-agnostic interface with two implementations:

* ``AnthropicProvider`` — calls the Anthropic API (official SDK). Used when
  ``AI_PROVIDER=anthropic`` and an API key is configured.
* ``FakeAIProvider`` — deterministic, no network. Used in tests and local
  development when ``AI_PROVIDER=fake`` (the default).

Every provider returns a :class:`ProviderResult` with parsed JSON plus usage
metadata (tokens, latency, model). Prompts containing user data are never
logged, and API keys are never exposed.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class ProviderError(Exception):
    """Base error for provider failures."""

    def __init__(self, code: str, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class ProviderUnavailableError(ProviderError):
    """The AI provider is unreachable or returned a non-retryable error."""


class ProviderRateLimitedError(ProviderError):
    """The AI provider rate-limited the request (HTTP 429)."""


class ProviderInvalidResponseError(ProviderError):
    """The AI provider returned a response that could not be parsed."""


class ProviderResult:
    """Structured result from an AI provider call."""

    def __init__(
        self,
        *,
        data: dict[str, Any],
        model: str,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        latency_ms: int | None = None,
    ) -> None:
        self.data = data
        self.model = model
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.latency_ms = latency_ms


class AIProvider(ABC):
    """Contract for a swappable AI provider."""

    @abstractmethod
    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        response_schema: type[Any],
    ) -> ProviderResult:
        """Generate a structured response from the provider.

        Args:
            system_prompt: System instruction (versioned, stored per analysis).
            user_payload: Minimal, safe data (no email/name/user id).
            response_schema: Pydantic model class used to validate output.

        Returns:
            ProviderResult with validated data and usage metadata.
        """


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider using the official anthropic SDK."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
        timeout_seconds: float | None = None,
        client: Any | None = None,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.ai_provider_api_key
        self.model = model or settings.ai_model
        self.max_tokens = max_tokens or settings.ai_max_tokens
        self.timeout_seconds = timeout_seconds or settings.ai_timeout_seconds
        self._client = client

        if not self.api_key:
            logger.warning(
                "AnthropicProvider initialized without API key; calls will fail."
            )

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        response_schema: type[Any],
    ) -> ProviderResult:
        """Call Anthropic Messages API with retries and structured output."""
        from anthropic import Anthropic, APIStatusError, APITimeoutError

        if self._client is not None:
            client: Anthropic = self._client
        else:
            client = Anthropic(api_key=self.api_key, timeout=self.timeout_seconds)

        user_message = json.dumps(user_payload, ensure_ascii=False)
        schema_name = getattr(response_schema, "__name__", "Schema")

        system_with_schema = (
            f"{system_prompt}\n\n"
            f"Respond ONLY with valid JSON matching this schema: {schema_name}. "
            "Do not include markdown fences, explanations, or extra text."
        )

        last_error: Exception | None = None
        for attempt in range(3):
            try:
                start = time.monotonic()
                response = client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=system_with_schema,
                    messages=[
                        {"role": "user", "content": user_message},
                    ],
                )
                latency_ms = int((time.monotonic() - start) * 1000)

                content = ""
                for block in response.content:
                    if block.type == "text":
                        content += block.text

                data = json.loads(content)

                usage = getattr(response, "usage", None)
                input_tokens = getattr(usage, "input_tokens", None) if usage else None
                output_tokens = (
                    getattr(usage, "output_tokens", None) if usage else None
                )

                return ProviderResult(
                    data=data,
                    model=self.model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    latency_ms=latency_ms,
                )

                # Note: validation (Pydantic) is done by the caller/service layer,
                # not here, so the provider stays thin.

            except APITimeoutError:
                last_error = ProviderUnavailableError(
                    "AI_PROVIDER_UNAVAILABLE",
                    "AI provider request timed out.",
                )
                logger.info("Anthropic timeout on attempt %s", attempt + 1)
            except APIStatusError as exc:
                if exc.status_code == 429:
                    last_error = ProviderRateLimitedError(
                        "AI_RATE_LIMITED",
                        "AI provider rate limit exceeded.",
                        status_code=429,
                    )
                elif exc.status_code >= 500:
                    last_error = ProviderUnavailableError(
                        "AI_PROVIDER_UNAVAILABLE",
                        f"AI provider returned HTTP {exc.status_code}.",
                        status_code=exc.status_code,
                    )
                else:
                    last_error = ProviderInvalidResponseError(
                        "AI_INVALID_RESPONSE",
                        f"AI provider returned HTTP {exc.status_code}.",
                        status_code=exc.status_code,
                    )
                logger.info(
                    "Anthropic status %s on attempt %s", exc.status_code, attempt + 1
                )
            except (json.JSONDecodeError, ValueError) as exc:
                last_error = ProviderInvalidResponseError(
                    "AI_INVALID_RESPONSE",
                    "AI provider returned unparseable JSON.",
                )
                logger.warning("Anthropic JSON parse error: %s", exc)
            except Exception as exc:  # pragma: no cover - defensive
                last_error = ProviderUnavailableError(
                    "AI_PROVIDER_UNAVAILABLE",
                    "AI provider request failed.",
                )
                logger.warning("Anthropic request error: %s", exc)

            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))

        assert last_error is not None
        raise last_error


class OpenRouterProvider(AIProvider):
    """OpenRouter provider using the OpenRouter chat completions API.

    Supports free models such as ``meta-llama/llama-3.1-8b-instruct:free``.
    Configured via ``OPENROUTER_API_KEY`` and ``OPENROUTER_MODEL`` env vars.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
        client: Any | None = None,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.openrouter_api_key
        self.model = model or settings.openrouter_model
        self.timeout_seconds = timeout_seconds or settings.openrouter_timeout_seconds
        self._client = client

        if not self.api_key:
            logger.warning(
                "OpenRouterProvider initialized without API key; calls will fail."
            )

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        response_schema: type[Any],
    ) -> ProviderResult:
        """Call OpenRouter chat completions API with retries and structured output."""
        user_message = json.dumps(user_payload, ensure_ascii=False)
        schema_name = getattr(response_schema, "__name__", "Schema")

        system_with_schema = (
            f"{system_prompt}\n\n"
            f"Respond ONLY with valid JSON matching this schema: {schema_name}. "
            "Do not include markdown fences, explanations, or extra text."
        )

        last_error: Exception | None = None
        for attempt in range(3):
            try:
                if self._client is not None:
                    client = self._client
                else:
                    client = httpx.AsyncClient(timeout=self.timeout_seconds)

                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_with_schema},
                            {"role": "user", "content": user_message},
                        ],
                        "temperature": 0.3,
                        "max_tokens": settings.ai_max_tokens,
                    },
                )

                if response.status_code == 429:
                    last_error = ProviderRateLimitedError(
                        "AI_RATE_LIMITED",
                        "OpenRouter rate limit exceeded.",
                        status_code=429,
                    )
                    logger.info("OpenRouter rate limited on attempt %s", attempt + 1)
                elif response.status_code >= 500:
                    last_error = ProviderUnavailableError(
                        "AI_PROVIDER_UNAVAILABLE",
                        f"OpenRouter returned HTTP {response.status_code}.",
                        status_code=response.status_code,
                    )
                    logger.info(
                        "OpenRouter server error %s on attempt %s",
                        response.status_code,
                        attempt + 1,
                    )
                elif response.status_code != 200:
                    last_error = ProviderInvalidResponseError(
                        "AI_INVALID_RESPONSE",
                        f"OpenRouter returned HTTP {response.status_code}.",
                        status_code=response.status_code,
                    )
                    logger.info(
                        "OpenRouter error %s on attempt %s",
                        response.status_code,
                        attempt + 1,
                    )
                else:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)

                    usage = data.get("usage", {})
                    return ProviderResult(
                        data=parsed,
                        model=self.model,
                        input_tokens=usage.get("prompt_tokens"),
                        output_tokens=usage.get("completion_tokens"),
                        latency_ms=0,
                    )

            except (httpx.TimeoutException, httpx.NetworkError):
                last_error = ProviderUnavailableError(
                    "AI_PROVIDER_UNAVAILABLE",
                    "OpenRouter request timed out or network error.",
                )
                logger.info("OpenRouter network error on attempt %s", attempt + 1)
            except (json.JSONDecodeError, ValueError) as exc:
                last_error = ProviderInvalidResponseError(
                    "AI_INVALID_RESPONSE",
                    "OpenRouter returned unparseable JSON.",
                )
                logger.warning("OpenRouter JSON parse error: %s", exc)
            except Exception as exc:  # pragma: no cover - defensive
                last_error = ProviderUnavailableError(
                    "AI_PROVIDER_UNAVAILABLE",
                    "OpenRouter request failed.",
                )
                logger.warning("OpenRouter request error: %s", exc)

            if attempt < 2:
                if self._client is None:
                    await client.aclose()
                await asyncio.sleep(0.5 * (attempt + 1))

        assert last_error is not None
        raise last_error


class FakeAIProvider(AIProvider):
    """Deterministic fake provider for tests and local development.

    Returns a plausible educational ingredient report without calling any
    network service. Selected automatically when AI_PROVIDER=fake.
    """

    def __init__(self, *, model: str = "fake-local") -> None:
        self.model = model

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        response_schema: type[Any],
    ) -> ProviderResult:
        """Build a deterministic report from the input payload."""
        ingredients = user_payload.get("ingredients", [])
        skin_type = user_payload.get("skin_type", "unknown")
        skin_concerns = user_payload.get("skin_concerns", [])

        key_ingredients: list[dict[str, Any]] = []
        for ing in ingredients[:6]:
            key_ingredients.append({
                "ingredient_id": str(ing.get("id", "")),
                "name": ing.get("name", "Unknown ingredient"),
                "role": ing.get("function", "other"),
                "explanation": (
                    f"{ing.get('name', 'This ingredient')} is listed in the "
                    "product formula. Based on our reference data, it serves a "
                    "general cosmetic function."
                ),
                "caution_level": "info",
            })

        cautions: list[str] = []
        if any("fragrance" in str(ing.get("name", "")).lower() for ing in ingredients):
            cautions.append(
                "Fragrance is present; people with sensitive skin may want to "
                "patch test first."
            )
        if any("alcohol" in str(ing.get("name", "")).lower() for ing in ingredients):
            cautions.append(
                "Alcohol is present; it can be drying for some skin types."
            )

        limitations: list[str] = [
            "Tevrox provides educational information about cosmetic ingredients. "
            "It is not medical advice and does not diagnose or treat any condition.",
            "This analysis is based on ingredient lists, not on product testing "
            "or clinical data.",
            "Individual skin reactions vary; consult a qualified professional "
            "for personal skin concerns.",
        ]

        data = {
            "summary": (
                f"This product contains {len(ingredients)} listed ingredient(s). "
                "The formula includes common cosmetic ingredients with typical "
                "functions such as hydration, preservation, and texture."
            ),
            "suitability_overview": (
                f"Based on your skin type ({skin_type}) and concerns "
                f"({', '.join(skin_concerns) if skin_concerns else 'none specified'}), "
                "review the cautions below before use."
            ),
            "key_ingredients": key_ingredients,
            "cautions": cautions,
            "limitations": limitations,
            "confidence": "medium",
            "confidence_reason": (
                "Deterministic fake report for development; not generated by a "
                "real AI model."
            ),
        }

        # Validate against the provided schema if it's a Pydantic model.
        if hasattr(response_schema, "model_validate"):
            data = response_schema.model_validate(data).model_dump()

        return ProviderResult(
            data=data,
            model=self.model,
            input_tokens=None,
            output_tokens=None,
            latency_ms=0,
        )


_provider: AIProvider | None = None
_provider_lock: Any = None

try:
    import threading

    _provider_lock = threading.Lock()
except Exception:  # pragma: no cover - threading always available
    _provider_lock = None


def get_ai_provider() -> AIProvider:
    """Return the configured AI provider (singleton per process)."""
    global _provider
    if _provider is None:
        if _provider_lock is not None:
            with _provider_lock:
                if _provider is None:
                    _provider = _build_provider()
        else:
            _provider = _build_provider()
    return _provider


def _build_provider() -> AIProvider:
    provider_name = settings.ai_provider.lower()
    if provider_name == "anthropic":
        return AnthropicProvider()
    if provider_name == "openrouter":
        return OpenRouterProvider()
    if provider_name == "fake":
        return FakeAIProvider()
    logger.warning(
        "Unknown AI_PROVIDER %r; falling back to FakeAIProvider", provider_name
    )
    return FakeAIProvider()


def set_ai_provider(provider: AIProvider | None) -> None:
    """Replace the process-wide provider (used by tests)."""
    global _provider
    if _provider_lock is not None:
        with _provider_lock:
            _provider = provider
    else:
        _provider = provider
