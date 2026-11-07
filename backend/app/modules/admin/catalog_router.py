"""Admin product and ingredient management endpoints (Phase 3)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.database.models import User
from app.database.session import get_db
from app.modules.admin.catalog_service import (
    add_alias,
    create_ingredient,
    list_ingredients,
    merge,
    update_ingredient,
)
from app.modules.ingredients.schemas import (
    IngredientAdminListResponse,
    IngredientAliasCreate,
    IngredientCreate,
    IngredientMergeRequest,
    IngredientMergeResponse,
    IngredientResponse,
    IngredientUpdate,
)
from app.modules.products.schemas import (
    AdminActionResponse,
    AdminProductCreate,
    AdminProductUpdate,
    ProductDetail,
    ProductListResponse,
    ProductVerificationRequest,
    ReviewQueueResponse,
)
from app.modules.products.service import (
    admin_create_product,
    admin_list_products,
    admin_review_queue,
    admin_set_verification,
    admin_soft_delete,
    admin_update_product,
)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_role("admin"))],
)
Db = Annotated[Session, Depends(get_db)]
AdminUser = Annotated[User, Depends(require_role("admin"))]


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------


@router.get("/products", response_model=ProductListResponse)
def list_admin_products(
    db: Db,
    verified_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> ProductListResponse:
    """List products for admin management, including unverified rows."""
    return admin_list_products(db, verified_only=verified_only, limit=limit, offset=offset)


@router.get("/products/review-queue", response_model=ReviewQueueResponse)
def review_queue(
    db: Db,
    source: str | None = Query(
        None, description="Filter by source: open_beauty_facts or user_submitted"
    ),
) -> ReviewQueueResponse:
    """Return unverified products awaiting review."""
    items = admin_review_queue(db, source_name=source)
    return ReviewQueueResponse(items=items, total=len(items), source=source)


@router.post("/products", response_model=ProductDetail, status_code=201)
def create_product(
    payload: AdminProductCreate,
    db: Db,
    actor: AdminUser,
) -> ProductDetail:
    """Create a product (admin only)."""
    return admin_create_product(db, actor=actor, payload=payload)


@router.put("/products/{product_id}", response_model=ProductDetail)
def update_product(
    product_id: UUID,
    payload: AdminProductUpdate,
    db: Db,
    actor: AdminUser,
) -> ProductDetail:
    """Edit a product (admin only)."""
    return admin_update_product(db, actor=actor, product_id=product_id, payload=payload)


@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: UUID, db: Db, actor: AdminUser) -> None:
    """Soft-delete a product by setting ``is_active`` to false."""
    admin_soft_delete(db, actor=actor, product_id=product_id)


@router.post("/products/{product_id}/verify", response_model=AdminActionResponse)
def verify_product(
    product_id: UUID,
    db: Db,
    actor: AdminUser,
    payload: ProductVerificationRequest | None = None,
) -> AdminActionResponse:
    """Verify a product and record an audit log entry."""
    product = admin_set_verification(
        db,
        actor=actor,
        product_id=product_id,
        status="verified",
        reason=payload.reason if payload else None,
    )
    return AdminActionResponse(
        message="Product verified",
        product_id=product.id,
        verification_status=product.verification_status,
    )


@router.post("/products/{product_id}/reject", response_model=AdminActionResponse)
def reject_product(
    product_id: UUID,
    db: Db,
    actor: AdminUser,
    payload: ProductVerificationRequest | None = None,
) -> AdminActionResponse:
    """Reject a product and record the optional reason in the audit log."""
    product = admin_set_verification(
        db,
        actor=actor,
        product_id=product_id,
        status="rejected",
        reason=payload.reason if payload else None,
    )
    return AdminActionResponse(
        message="Product rejected",
        product_id=product.id,
        verification_status=product.verification_status,
    )


# ---------------------------------------------------------------------------
# Ingredients
# ---------------------------------------------------------------------------


@router.get("/ingredients", response_model=IngredientAdminListResponse)
def admin_list_ingredients(
    db: Db,
    q: str | None = Query(None, min_length=1, max_length=300),
    unreviewed: bool = Query(False, description="Only show ingredients awaiting review"),
    include_inactive: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> IngredientAdminListResponse:
    """List ingredients, optionally filtering to unreviewed rows."""
    items, total = list_ingredients(
        db,
        q=q,
        unreviewed_only=unreviewed,
        include_inactive=include_inactive,
        limit=limit,
        offset=offset,
    )
    return IngredientAdminListResponse(
        items=[IngredientResponse.model_validate(item) for item in items],
        total=total,
        unreviewed_only=unreviewed,
    )


@router.get("/ingredients/unreviewed", response_model=IngredientAdminListResponse)
def admin_unreviewed_ingredients(
    db: Db,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> IngredientAdminListResponse:
    """Convenience endpoint for the unreviewed-ingredient queue."""
    items, total = list_ingredients(
        db, unreviewed_only=True, limit=limit, offset=offset
    )
    return IngredientAdminListResponse(
        items=[IngredientResponse.model_validate(item) for item in items],
        total=total,
        unreviewed_only=True,
    )


@router.post("/ingredients", response_model=IngredientResponse, status_code=201)
def create_ingredient_endpoint(
    payload: IngredientCreate,
    db: Db,
    actor: AdminUser,
) -> IngredientResponse:
    """Create a reviewed ingredient."""
    ingredient = create_ingredient(db, actor=actor, payload=payload)
    return IngredientResponse.model_validate(ingredient)


@router.post("/ingredients/merge", response_model=IngredientMergeResponse)
def merge_ingredients_endpoint(
    payload: IngredientMergeRequest,
    db: Db,
    actor: AdminUser,
) -> IngredientMergeResponse:
    """Merge a duplicate ingredient into a target ingredient."""
    result = merge(
        db,
        actor=actor,
        source_id=payload.source_id,
        target_id=payload.target_id,
    )
    return IngredientMergeResponse(
        message="Ingredients merged",
        source_id=result["source_id"],
        target_id=result["target_id"],
        moved_product_ingredients=result["moved_product_ingredients"],
        dropped_duplicate_links=result["dropped_duplicate_links"],
        moved_aliases=result["moved_aliases"],
    )


@router.put("/ingredients/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient_endpoint(
    ingredient_id: UUID,
    payload: IngredientUpdate,
    db: Db,
    actor: AdminUser,
) -> IngredientResponse:
    """Edit an ingredient or mark it reviewed."""
    ingredient = update_ingredient(
        db, actor=actor, ingredient_id=ingredient_id, payload=payload
    )
    return IngredientResponse.model_validate(ingredient)


@router.post(
    "/ingredients/{ingredient_id}/aliases",
    response_model=dict,
    status_code=201,
)
def add_alias_endpoint(
    ingredient_id: UUID,
    payload: IngredientAliasCreate,
    db: Db,
    actor: AdminUser,
) -> dict:
    """Add an alias to an ingredient."""
    if payload.ingredient_id != ingredient_id:
        raise HTTPException(400, "ingredient_id in the body must match the path")
    alias = add_alias(db, actor=actor, ingredient_id=ingredient_id, alias=payload.alias)
    return {"id": str(alias.id), "alias_normalized": alias.alias_normalized}
