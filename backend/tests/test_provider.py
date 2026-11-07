"""External provider mapping, resilience, and caching tests (no real network)."""

from __future__ import annotations

import asyncio
from typing import Any

import httpx
import pytest

from app.integrations.product_provider import (
    ExternalProductDTO,
    OpenBeautyFactsProvider,
    map_external_category,
    map_open_beauty_facts_payload,
)


def _valid_payload() -> dict[str, Any]:
    return {
        "product": {
            "code": "12345678",
            "product_name": "Hydrating Serum",
            "brands": "Example Brand",
            "categories": "Face serums",
            "ingredients_text": "Aqua, Glycerin, Niacinamide",
            "image_url": "https://images.example/serum.jpg",
            "quantity": "30 ml",
        }
    }


def test_map_valid_payload() -> None:
    dto = map_open_beauty_facts_payload(_valid_payload(), barcode="12345678")

    assert isinstance(dto, ExternalProductDTO)
    assert dto.name == "Hydrating Serum"
    assert dto.brand == "Example Brand"
    assert dto.category == "serum"
    assert dto.ingredients_text == "Aqua, Glycerin, Niacinamide"
    assert dto.image_url == "https://images.example/serum.jpg"


@pytest.mark.parametrize(
    "payload",
    [
        None,
        {},
        {"product": None},
        {"product": "not-a-dict"},
        {"product": {"product_name": ""}},
        {"product": {"product_name": 123}},
    ],
)
def test_map_malformed_payload_returns_none(payload: Any) -> None:
    assert map_open_beauty_facts_payload(payload) is None


def test_map_rejects_non_http_image_and_recovers_barcode() -> None:
    payload = _valid_payload()
    payload["product"]["image_url"] = "javascript:alert(1)"
    payload["product"].pop("code")

    dto = map_open_beauty_facts_payload(payload, barcode="99999999")

    assert dto is not None
    assert dto.image_url is None
    assert dto.barcode == "99999999"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Sunscreens, Sun protection", "sunscreen"),
        ("Face cleansers", "cleanser"),
        ("Toners", "toner"),
        ("Serums", "serum"),
        ("Moisturizers", "moisturizer"),
        ("Face masks", "mask"),
        ("Scrubs & exfoliants", "exfoliant"),
        ("Eye contour", "eye_care"),
        ("Acne treatments", "treatment"),
        ("Something else", "other"),
        (None, "other"),
    ],
)
def test_category_mapping(raw: str | None, expected: str) -> None:
    assert map_external_category(raw) == expected


def test_provider_lookup_uses_response_and_cache() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return httpx.Response(200, json=_valid_payload())

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            provider = OpenBeautyFactsProvider(
                client=http, cache_ttl_seconds=60, timeout_seconds=1
            )
            first = await provider.lookup_by_barcode("12345678")
            second = await provider.lookup_by_barcode("12345678")

            assert first is not None and first.name == "Hydrating Serum"
            assert second is not None and second.name == "Hydrating Serum"

    asyncio.run(run())
    assert calls["count"] == 1


def test_provider_returns_none_for_404() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"status": 404})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            provider = OpenBeautyFactsProvider(client=http, timeout_seconds=1)
            assert await provider.lookup_by_barcode("00000000") is None

    asyncio.run(run())


def test_provider_retries_server_errors_then_returns_none() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return httpx.Response(500, json={"error": "boom"})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            provider = OpenBeautyFactsProvider(client=http, timeout_seconds=1)
            assert await provider.lookup_by_barcode("11111111") is None

    asyncio.run(run())
    assert calls["count"] == 2


def test_provider_swallows_timeouts() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out", request=request)

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            provider = OpenBeautyFactsProvider(client=http, timeout_seconds=1)
            assert await provider.lookup_by_barcode("22222222") is None

    asyncio.run(run())


def test_provider_search_maps_results() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "products": [
                    {"product_name": "Search Serum", "categories": "Serums"},
                    {"product_name": ""},
                    "malformed",
                ]
            },
        )

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            provider = OpenBeautyFactsProvider(client=http, timeout_seconds=1)
            results = await provider.search("serum", limit=10)
            assert [item.name for item in results] == ["Search Serum"]

    asyncio.run(run())
