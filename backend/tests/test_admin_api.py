"""Admin catalogue authorization, verification, audit, and ingredient tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.database.models import User
from app.modules.products.service import create_user_submission

from .conftest import auth_headers
from .test_products_api import create_product


def test_admin_endpoints_reject_regular_users(
    client: TestClient, user_token: str
) -> None:
    headers = auth_headers(user_token)

    assert client.get("/api/v1/admin/products", headers=headers).status_code == 403
    assert client.get("/api/v1/admin/ingredients", headers=headers).status_code == 403
    assert (
        client.get("/api/v1/admin/products/review-queue", headers=headers).status_code
        == 403
    )


def test_admin_endpoints_reject_anonymous(client: TestClient) -> None:
    assert client.get("/api/v1/admin/products").status_code == 401


def test_review_queue_lists_unverified_products(
    client: TestClient, admin_token: str
) -> None:
    create_product(client, admin_token, name="Verified", status="verified")
    create_product(client, admin_token, name="Pending", status="unverified")

    response = client.get(
        "/api/v1/admin/products/review-queue", headers=auth_headers(admin_token)
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["name"] == "Pending"


def test_verify_and_reject_create_audit_logs(
    client: TestClient, admin_token: str
) -> None:
    first = create_product(
        client, admin_token, name="To Verify", status="unverified"
    )
    second = create_product(
        client, admin_token, name="To Reject", status="unverified"
    )
    headers = auth_headers(admin_token)

    verified = client.post(
        f"/api/v1/admin/products/{first['id']}/verify",
        headers=headers,
        json={"reason": "label checked"},
    )
    assert verified.status_code == 200, verified.text
    assert verified.json()["verification_status"] == "verified"

    rejected = client.post(
        f"/api/v1/admin/products/{second['id']}/reject",
        headers=headers,
        json={"reason": "duplicate"},
    )
    assert rejected.status_code == 200, rejected.text
    assert rejected.json()["verification_status"] == "rejected"

    detail = client.get(
        f"/api/v1/products/{first['id']}", headers=headers
    ).json()
    assert detail["verified_by"] is not None
    assert detail["verified_at"] is not None

    logs = client.get("/api/v1/admin/audit-logs", headers=headers).json()
    actions = {log["action"] for log in logs["logs"]}
    assert "product_create" in actions
    assert "product_verified" in actions
    assert "product_rejected" in actions
    assert logs["total"] >= 4


def test_admin_update_and_soft_delete(
    client: TestClient, admin_token: str
) -> None:
    product = create_product(
        client, admin_token, name="Old Name", category="other"
    )
    headers = auth_headers(admin_token)

    updated = client.put(
        f"/api/v1/admin/products/{product['id']}",
        headers=headers,
        json={
            "name": "New Name",
            "category": "serum",
            "ingredients_raw_text": "Aqua, Glycerin",
        },
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["name"] == "New Name"
    assert len(updated.json()["ingredients"]) == 2

    deleted = client.delete(
        f"/api/v1/admin/products/{product['id']}", headers=headers
    )
    assert deleted.status_code == 204
    assert (
        client.get(f"/api/v1/products/{product['id']}", headers=headers).status_code
        == 404
    )

    logs = client.get("/api/v1/admin/audit-logs", headers=headers).json()
    actions = {log["action"] for log in logs["logs"]}
    assert "product_update" in actions
    assert "product_soft_delete" in actions


def test_admin_duplicate_barcode_conflict(
    client: TestClient, admin_token: str
) -> None:
    create_product(client, admin_token, name="First", barcode="12345670")

    response = client.post(
        "/api/v1/admin/products",
        headers=auth_headers(admin_token),
        json={
            "name": "Second",
            "category": "other",
            "barcode": "12345670",
            "verification_status": "unverified",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PRODUCT_ALREADY_EXISTS"


def test_ingredient_admin_crud_and_unreviewed_queue(
    client: TestClient, admin_token: str
) -> None:
    headers = auth_headers(admin_token)

    created = client.post(
        "/api/v1/admin/ingredients",
        headers=headers,
        json={
            "name": "Niacinamide",
            "description": "Brightening active",
            "category_function": "active",
            "is_reviewed": False,
        },
    )
    assert created.status_code == 201, created.text
    ingredient = created.json()
    assert ingredient["normalized_name"] == "niacinamide"
    assert ingredient["is_reviewed"] is False

    unreviewed = client.get(
        "/api/v1/admin/ingredients/unreviewed", headers=headers
    ).json()
    assert unreviewed["total"] == 1

    updated = client.put(
        f"/api/v1/admin/ingredients/{ingredient['id']}",
        headers=headers,
        json={"is_reviewed": True, "description": "Reviewed"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["is_reviewed"] is True

    alias = client.post(
        f"/api/v1/admin/ingredients/{ingredient['id']}/aliases",
        headers=headers,
        json={"ingredient_id": ingredient["id"], "alias": "Vitamin B3"},
    )
    assert alias.status_code == 201, alias.text
    assert alias.json()["alias_normalized"] == "vitamin b3"

    duplicate_alias = client.post(
        f"/api/v1/admin/ingredients/{ingredient['id']}/aliases",
        headers=headers,
        json={"ingredient_id": ingredient["id"], "alias": "Vitamin B3"},
    )
    assert duplicate_alias.status_code == 409

    search = client.get(
        "/api/v1/ingredients/search",
        params={"q": "Vitamin B3"},
        headers=headers,
    ).json()
    assert search[0]["id"] == ingredient["id"]

    logs = client.get("/api/v1/admin/audit-logs", headers=headers).json()
    actions = {log["action"] for log in logs["logs"]}
    assert "ingredient_create" in actions
    assert "ingredient_update" in actions
    assert "ingredient_alias_create" in actions


def test_ingredient_merge_endpoint_moves_links(
    client: TestClient, admin_token: str
) -> None:
    headers = auth_headers(admin_token)

    def create_ingredient(name: str) -> dict:
        response = client.post(
            "/api/v1/admin/ingredients",
            headers=headers,
            json={"name": name, "category_function": "other", "is_reviewed": True},
        )
        assert response.status_code == 201, response.text
        return response.json()

    source = create_ingredient("Water")
    target = create_ingredient("Aqua")

    product = create_product(
        client,
        admin_token,
        name="Merged Product",
        ingredients="Water, Glycerin",
    )
    product_links = {
        link["name"] for link in product["ingredients"]
    }
    assert "Water" in product_links

    merged = client.post(
        "/api/v1/admin/ingredients/merge",
        headers=headers,
        json={"source_id": source["id"], "target_id": target["id"]},
    )
    assert merged.status_code == 200, merged.text
    body = merged.json()
    assert body["moved_product_ingredients"] == 1

    detail = client.get(
        f"/api/v1/products/{product['id']}", headers=headers
    ).json()
    ingredient_names = {link["name"] for link in detail["ingredients"]}
    assert "Aqua" in ingredient_names
    assert "Water" not in ingredient_names

    source_rows = client.get(
        "/api/v1/admin/ingredients",
        params={"include_inactive": True, "q": "Water"},
        headers=headers,
    ).json()
    assert source_rows["items"][0]["is_active"] is False

    logs = client.get("/api/v1/admin/audit-logs", headers=headers).json()
    assert any(log["action"] == "ingredient_merge" for log in logs["logs"])


def test_merge_validation_errors(
    client: TestClient, admin_token: str
) -> None:
    headers = auth_headers(admin_token)
    created = client.post(
        "/api/v1/admin/ingredients",
        headers=headers,
        json={"name": "Self Merge", "category_function": "other"},
    ).json()

    response = client.post(
        "/api/v1/admin/ingredients/merge",
        headers=headers,
        json={"source_id": created["id"], "target_id": created["id"]},
    )
    assert response.status_code == 400


def test_admin_service_submission_helper_marks_unverified(
    client: TestClient, admin_token: str, session_factory
) -> None:
    # The helper used by the API is exercised directly here to confirm the
    # database row is unverified even when a trusted caller is used.
    with session_factory() as db:
        user = db.query(User).filter(User.email == "admin@example.com").one()
        product = create_user_submission(
            db,
            user=user,
            name="Direct Helper Product",
            category="other",
            barcode=None,
            brand_name=None,
            ingredients_raw_text="Aqua",
        )
        assert str(product.verification_status) == "unverified"
