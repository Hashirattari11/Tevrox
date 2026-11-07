"""Product catalogue API tests: search, barcode, submissions, admin flows."""

from __future__ import annotations

from typing import Any

import httpx
from fastapi.testclient import TestClient

from app.integrations.product_provider import ExternalProductDTO, set_product_provider
from app.modules.ingredients.service import parse_ingredient_list

from .conftest import auth_headers


class FakeProvider:
    """Deterministic provider double; never performs network I/O."""

    def __init__(
        self,
        dto: ExternalProductDTO | None = None,
        error: Exception | None = None,
    ) -> None:
        self.dto = dto
        self.error = error
        self.calls = 0

    async def lookup_by_barcode(self, code: str) -> ExternalProductDTO | None:
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.dto

    async def search(self, query: str, limit: int = 20) -> list[ExternalProductDTO]:
        if self.error is not None:
            raise self.error
        return [self.dto] if self.dto else []


def create_product(
    client: TestClient,
    admin_token: str,
    *,
    name: str,
    category: str = "other",
    barcode: str | None = None,
    brand_name: str | None = None,
    ingredients: str | None = None,
    status: str = "verified",
) -> dict[str, Any]:
    response = client.post(
        "/api/v1/admin/products",
        headers=auth_headers(admin_token),
        json={
            "name": name,
            "category": category,
            "barcode": barcode,
            "brand_name": brand_name,
            "ingredients_raw_text": ingredients,
            "verification_status": status,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_product_endpoints_require_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/products").status_code == 401


def test_search_filters_and_defaults_to_verified(
    client: TestClient, admin_token: str
) -> None:
    create_product(
        client,
        admin_token,
        name="CeraVe Moisturising Cream",
        category="moisturizer",
        brand_name="CeraVe",
    )
    create_product(
        client,
        admin_token,
        name="The Ordinary Niacinamide Serum",
        category="serum",
        brand_name="The Ordinary",
    )
    create_product(
        client,
        admin_token,
        name="Hidden Mystery Cream",
        category="moisturizer",
        brand_name="Mystery",
        status="unverified",
    )

    headers = auth_headers(admin_token)

    verified = client.get("/api/v1/products", headers=headers).json()
    assert verified["total"] == 2
    assert all(item["verification_status"] == "verified" for item in verified["items"])

    everything = client.get(
        "/api/v1/products", params={"verified_only": False}, headers=headers
    ).json()
    assert everything["total"] == 3

    by_query = client.get(
        "/api/v1/products", params={"q": "cream"}, headers=headers
    ).json()
    assert [item["name"] for item in by_query["items"]] == ["CeraVe Moisturising Cream"]

    by_category = client.get(
        "/api/v1/products", params={"category": "serum"}, headers=headers
    ).json()
    assert by_category["total"] == 1

    by_brand = client.get(
        "/api/v1/products", params={"brand": "cerave"}, headers=headers
    ).json()
    assert by_brand["total"] == 1
    assert by_brand["items"][0]["brand"]["name"] == "CeraVe"


def test_pagination_with_cursor(client: TestClient, admin_token: str) -> None:
    for index in range(5):
        create_product(
            client,
            admin_token,
            name=f"Product {index}",
            category="other",
        )

    headers = auth_headers(admin_token)
    first = client.get(
        "/api/v1/products", params={"limit": 2}, headers=headers
    ).json()
    assert first["total"] == 5
    assert len(first["items"]) == 2
    assert first["next_cursor"]

    second = client.get(
        "/api/v1/products",
        params={"limit": 2, "cursor": first["next_cursor"]},
        headers=headers,
    ).json()
    assert len(second["items"]) == 2
    assert {i["id"] for i in first["items"]}.isdisjoint({i["id"] for i in second["items"]})

    last = client.get(
        "/api/v1/products",
        params={"limit": 2, "cursor": second["next_cursor"]},
        headers=headers,
    ).json()
    assert len(last["items"]) == 1
    assert last["next_cursor"] is None


def test_invalid_cursor_returns_structured_error(
    client: TestClient, admin_token: str
) -> None:
    response = client.get(
        "/api/v1/products",
        params={"cursor": "!!not-base64!!"},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_CURSOR"


def test_categories_and_brands_endpoints(
    client: TestClient, admin_token: str
) -> None:
    create_product(
        client,
        admin_token,
        name="Cleanser",
        category="cleanser",
        brand_name="Brandy",
    )
    headers = auth_headers(admin_token)

    categories = client.get("/api/v1/products/categories", headers=headers)
    assert categories.status_code == 200
    counts = {item["category"]: item["count"] for item in categories.json()["categories"]}
    assert counts["cleanser"] == 1

    brands = client.get("/api/v1/brands", params={"q": "brand"}, headers=headers)
    assert brands.status_code == 200
    assert brands.json()[0]["name"] == "Brandy"


def test_barcode_found_internal_database(
    client: TestClient, admin_token: str
) -> None:
    created = create_product(
        client,
        admin_token,
        name="Internal Product",
        barcode="12345678",
        ingredients="Aqua, Glycerin",
    )

    response = client.get(
        "/api/v1/products/barcode/12345678", headers=auth_headers(admin_token)
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert len(body["ingredients"]) == 2


def test_barcode_found_external_provider_stored_unverified(
    client: TestClient, admin_token: str
) -> None:
    provider = FakeProvider(
        dto=ExternalProductDTO(
            barcode="87654321",
            name="External Serum",
            brand="External Brand",
            category="serum",
            ingredients_text="Aqua, Niacinamide",
        )
    )
    set_product_provider(provider)  # type: ignore[arg-type]

    response = client.get(
        "/api/v1/products/barcode/87654321", headers=auth_headers(admin_token)
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["name"] == "External Serum"
    assert body["verification_status"] == "unverified"
    assert body["source"]["name"] == "open_beauty_facts"
    assert len(body["ingredients"]) == 2
    assert provider.calls == 1

    # A second lookup is served by the internal database, not the provider.
    again = client.get(
        "/api/v1/products/barcode/87654321", headers=auth_headers(admin_token)
    )
    assert again.status_code == 200
    assert provider.calls == 1


def test_barcode_not_found_returns_hint(
    client: TestClient, admin_token: str
) -> None:
    set_product_provider(FakeProvider(dto=None))  # type: ignore[arg-type]

    response = client.get(
        "/api/v1/products/barcode/11112222", headers=auth_headers(admin_token)
    )

    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "PRODUCT_NOT_FOUND"
    assert "submit" in error["details"]["hint"].lower()


def test_barcode_provider_timeout_is_not_a_server_error(
    client: TestClient, admin_token: str
) -> None:
    set_product_provider(
        FakeProvider(error=httpx.TimeoutException("timed out"))  # type: ignore[arg-type]
    )

    response = client.get(
        "/api/v1/products/barcode/33334444", headers=auth_headers(admin_token)
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND"


def test_barcode_incomplete_external_record_returns_not_found(
    client: TestClient, admin_token: str
) -> None:
    set_product_provider(
        FakeProvider(dto=ExternalProductDTO(barcode="55556666", name=None))  # type: ignore[arg-type]
    )

    response = client.get(
        "/api/v1/products/barcode/55556666", headers=auth_headers(admin_token)
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND"


def test_barcode_validation_rejects_bad_length(
    client: TestClient, admin_token: str
) -> None:
    response = client.get(
        "/api/v1/products/barcode/123", headers=auth_headers(admin_token)
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_BARCODE"


def test_submission_creates_unverified_product_with_ingredients(
    client: TestClient, user_token: str
) -> None:
    response = client.post(
        "/api/v1/products/submissions",
        headers=auth_headers(user_token),
        json={
            "name": "User Submitted Serum",
            "brand_name": "User Brand",
            "category": "serum",
            "barcode": "99990000",
            "ingredients_raw_text": "Aqua, Glycerin, Mystery Extract",
        },
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["verification_status"] == "unverified"
    assert "review" in body["message"].lower()

    detail = client.get(
        f"/api/v1/products/{body['id']}", headers=auth_headers(user_token)
    ).json()
    assert len(detail["ingredients"]) == 3


def test_submission_duplicate_barcode_conflict(
    client: TestClient, user_token: str, admin_token: str
) -> None:
    create_product(
        client, admin_token, name="Existing", barcode="77778888"
    )

    response = client.post(
        "/api/v1/products/submissions",
        headers=auth_headers(user_token),
        json={
            "name": "Duplicate",
            "category": "other",
            "barcode": "77778888",
            "ingredients_raw_text": "Aqua",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PRODUCT_ALREADY_EXISTS"


def test_submission_rate_limit(client: TestClient, user_token: str) -> None:
    payload = {
        "name": "Rate Limited",
        "category": "other",
        "ingredients_raw_text": "Aqua",
    }
    for index in range(3):
        payload["name"] = f"Rate Limited {index}"
        response = client.post(
            "/api/v1/products/submissions",
            headers=auth_headers(user_token),
            json=payload,
        )
        assert response.status_code == 201, response.text

    blocked = client.post(
        "/api/v1/products/submissions",
        headers=auth_headers(user_token),
        json=payload,
    )
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "RATE_LIMITED"


def test_submission_rejects_blank_ingredients(
    client: TestClient, user_token: str
) -> None:
    response = client.post(
        "/api/v1/products/submissions",
        headers=auth_headers(user_token),
        json={"name": "Blank", "category": "other", "ingredients_raw_text": "   "},
    )
    assert response.status_code == 422


def test_parsed_submission_ingredients_include_unknowns(
    client: TestClient, user_token: str
) -> None:
    parsed = parse_ingredient_list("Aqua, Strange New Ingredient")
    assert [entry["normalized"] for entry in parsed] == [
        "aqua",
        "strange new ingredient",
    ]
