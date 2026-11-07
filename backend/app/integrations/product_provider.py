"""External product catalogue provider contract and Open Beauty Facts client.

External data is always untrusted. The provider validates and maps the remote
payload into :class:`ExternalProductDTO`; malformed or missing fields are
discarded and every failure degrades to ``None`` instead of raising.
"""

from __future__ import annotations

import logging
import re
import threading
import time
from abc import ABC, abstractmethod
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from app.core.config import get_settings

logger = logging.getLogger(__name__)

CATEGORY_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("sunscreen", ("sunscreen", "sun screen", "sunblock", "spf", "sun care", "sun-care")),
    ("cleanser", ("cleanser", "cleaner", "face wash", "foam", "micellar", "makeup remover")),
    ("toner", ("toner", "tonic", "lotions/tonics")),
    ("serum", ("serum", "serums", "ampoule", "essence")),
    ("moisturizer", ("moisturizer", "moisturiser", "cream", "lotion", "emulsion", "gel cream")),
    ("mask", ("mask", "masks", "face pack")),
    ("exfoliant", ("exfoliant", "exfoliator", "scrub", "peeling", "peel")),
    ("eye_care", ("eye care", "eye cream", "eye contour", "eye serum")),
    ("treatment", ("treatment", "spot", "acne", "retinol", "patch")),
)
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


class ExternalProductDTO(BaseModel):
    """Normalized, validated view of a product returned by an external API."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    barcode: str | None = Field(default=None, max_length=32)
    name: str | None = Field(default=None, max_length=300)
    brand: str | None = Field(default=None, max_length=200)
    categories: str | None = Field(default=None, max_length=500)
    category: str = "other"
    ingredients_text: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    quantity: str | None = Field(default=None, max_length=120)
    source: str = "open_beauty_facts"
    raw: dict[str, Any] = Field(default_factory=dict, exclude=True)

    @property
    def display_name(self) -> str | None:
        return self.name.strip() if self.name else None


def map_external_category(raw_categories: str | None) -> str:
    """Map a free-text external category list onto the internal enum values."""
    if not raw_categories:
        return "other"
    lowered = raw_categories.lower()
    for category, keywords in CATEGORY_KEYWORDS:
        if any(keyword in lowered for keyword in keywords):
            return category
    return "other"


def _clean_text(value: Any, max_length: int) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = re.sub(r"\s+", " ", value).strip()
    if not cleaned:
        return None
    return cleaned[:max_length]


def map_open_beauty_facts_payload(
    payload: Any, *, barcode: str | None = None
) -> ExternalProductDTO | None:
    """Map an Open Beauty Facts payload to a DTO without trusting its shape."""
    if not isinstance(payload, dict):
        return None
    product = payload.get("product")
    if not isinstance(product, dict):
        return None

    name = _clean_text(
        product.get("product_name") or product.get("product_name_en") or product.get("name"),
        300,
    )
    if not name:
        return None

    raw_categories = _clean_text(product.get("categories"), 500)
    ingredients = (
        _clean_text(product.get("ingredients_text"), 100_000)
        or _clean_text(product.get("ingredients_text_en"), 100_000)
        or _clean_text(product.get("ingredients_text_with_allergens"), 100_000)
    )
    image_url = _clean_text(
        product.get("image_url") or product.get("image_front_url"), 500
    )
    if image_url and not image_url.startswith(("http://", "https://")):
        image_url = None

    code = _clean_text(product.get("code"), 32) or barcode

    try:
        return ExternalProductDTO(
            barcode=code,
            name=name,
            brand=_clean_text(product.get("brands"), 200),
            categories=raw_categories,
            category=map_external_category(raw_categories),
            ingredients_text=ingredients,
            image_url=image_url,
            quantity=_clean_text(product.get("quantity"), 120),
            source="open_beauty_facts",
            raw=product,
        )
    except Exception:  # pragma: no cover - defensive, pydantic handles most cases
        logger.warning("Discarding malformed external product payload", exc_info=True)
        return None


class ProductProvider(ABC):
    """Contract for a swappable external product catalogue."""

    @abstractmethod
    async def lookup_by_barcode(self, code: str) -> ExternalProductDTO | None:
        """Return a normalized product for a barcode, or ``None``."""

    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> list[ExternalProductDTO]:
        """Return normalized products matching a free-text query."""


class _TTLCache:
    """Small thread-safe in-memory TTL cache.

    Production should replace this with Redis so multiple API workers share
    cached provider responses (documented in ``docs/architecture/decisions.md``).
    """

    def __init__(self, ttl_seconds: int) -> None:
        self._ttl = ttl_seconds
        self._data: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        now = time.monotonic()
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at <= now:
                self._data.pop(key, None)
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        if self._ttl <= 0:
            return
        with self._lock:
            self._data[key] = (time.monotonic() + self._ttl, value)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()


class OpenBeautyFactsProvider(ProductProvider):
    """Open Beauty Facts API client (provisional provider for Phase 3)."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
        cache_ttl_seconds: int | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.open_beauty_facts_base_url).rstrip("/")
        self.timeout_seconds = timeout_seconds or settings.product_provider_timeout_seconds
        self.user_agent = settings.product_user_agent
        self._client = client
        self._cache = _TTLCache(
            cache_ttl_seconds
            if cache_ttl_seconds is not None
            else settings.product_provider_cache_ttl_seconds
        )

    async def _request_json(self, url: str, params: dict[str, Any] | None = None) -> Any | None:
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }
        last_error: Exception | None = None
        for _attempt in range(2):
            try:
                if self._client is not None:
                    response = await self._client.get(
                        url, params=params, headers=headers, timeout=self.timeout_seconds
                    )
                else:
                    async with httpx.AsyncClient(
                        timeout=httpx.Timeout(self.timeout_seconds)
                    ) as client:
                        response = await client.get(url, params=params, headers=headers)
                if response.status_code == 404:
                    return None
                if response.status_code >= 500:
                    last_error = httpx.HTTPStatusError(
                        f"Provider returned {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                    continue
                if response.status_code != 200:
                    logger.info("Product provider returned HTTP %s", response.status_code)
                    return None
                return response.json()
            except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPError) as exc:
                last_error = exc
                continue
            except Exception:
                logger.warning("Product provider request failed", exc_info=True)
                return None
        if last_error is not None:
            logger.info("Product provider unavailable after retry: %s", last_error)
        return None

    async def lookup_by_barcode(self, code: str) -> ExternalProductDTO | None:
        cache_key = f"barcode:{code}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        url = f"{self.base_url}/api/v3/product/{code}.json"
        payload = await self._request_json(url, params={"counters": "1"})
        dto = map_open_beauty_facts_payload(payload, barcode=code)
        if dto is not None:
            self._cache.set(cache_key, dto)
        return dto

    async def search(self, query: str, limit: int = 20) -> list[ExternalProductDTO]:
        cache_key = f"search:{query.lower()}:{limit}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        url = f"{self.base_url}/cgi/search.pl"
        payload = await self._request_json(
            url,
            params={
                "search_terms": query,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": max(1, min(limit, 50)),
            },
        )
        if not isinstance(payload, dict):
            return []
        products = payload.get("products")
        if not isinstance(products, list):
            return []

        results: list[ExternalProductDTO] = []
        for item in products[:limit]:
            dto = map_open_beauty_facts_payload({"product": item})
            if dto is not None:
                results.append(dto)
        self._cache.set(cache_key, results)
        return results


_provider: ProductProvider | None = None
_provider_lock = threading.Lock()


def get_product_provider() -> ProductProvider:
    global _provider
    if _provider is None:
        with _provider_lock:
            if _provider is None:
                _provider = OpenBeautyFactsProvider()
    return _provider


def set_product_provider(provider: ProductProvider | None) -> None:
    """Replace the process-wide provider (used by tests and future adapters)."""
    global _provider
    with _provider_lock:
        _provider = provider
