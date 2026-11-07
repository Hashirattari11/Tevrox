from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.models import User
from app.database.session import get_db
from app.modules.products.schemas import (
    BrandResponse,
    CategoriesResponse,
    ProductDetail,
    ProductListResponse,
    ProductSubmissionCreate,
    ProductSubmissionResponse,
)
from app.modules.products.service import (
    create_user_submission,
    get_product_by_id,
    list_brands,
    list_categories,
    lookup_barcode,
    search_products,
)

router = APIRouter(prefix="/products", tags=["products"])
brands_router = APIRouter(prefix="/brands", tags=["products"])
Db = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=ProductListResponse)
def list_products(
    db: Db,
    _user: CurrentUser,
    q: str | None = Query(None, min_length=1, max_length=300),
    category: str | None = Query(None, max_length=80),
    brand: str | None = Query(None, max_length=200),
    verified_only: bool = Query(
        True, description="Only verified products by default; set false to include unverified"
    ),
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = Query(None, description="Opaque cursor from a previous response"),
    offset: int | None = Query(None, ge=0, description="Optional offset alternative to cursor"),
) -> ProductListResponse:
    """Search the catalogue with filters and cursor pagination."""
    return search_products(
        db,
        q=q,
        category=category,
        brand=brand,
        verified_only=verified_only,
        limit=limit,
        cursor=cursor,
        offset=offset,
    )


@router.get("/categories", response_model=CategoriesResponse)
def get_categories(db: Db, _user: CurrentUser) -> CategoriesResponse:
    """List product categories with counts."""
    return CategoriesResponse(categories=list_categories(db))


@router.post(
    "/submissions",
    response_model=ProductSubmissionResponse,
    status_code=201,
    description="Submit an unknown product for admin review",
)
def submit_product(
    payload: ProductSubmissionCreate,
    db: Db,
    user: CurrentUser,
) -> ProductSubmissionResponse:
    """Submit a product that is missing from the catalogue."""
    product = create_user_submission(
        db,
        user=user,
        name=payload.name,
        category=payload.category,
        barcode=payload.barcode,
        brand_name=payload.brand_name,
        ingredients_raw_text=payload.ingredients_raw_text,
    )
    return ProductSubmissionResponse(
        id=product.id,
        name=product.name,
        barcode=product.barcode,
        category=product.category or "other",
        verification_status=str(product.verification_status),
        message=(
            "Product submitted for review. An admin will verify or reject it; "
            "until then it is clearly labelled as unverified."
        ),
    )


@router.get("/barcode/{code}", response_model=ProductDetail)
async def get_product_by_barcode(code: str, db: Db, _user: CurrentUser) -> ProductDetail:
    """Look up a barcode internally, then externally, then store as unverified."""
    return await lookup_barcode(db, code)


@router.get("/{product_id}", response_model=ProductDetail)
def get_product(product_id: UUID, db: Db, _user: CurrentUser) -> ProductDetail:
    """Return a product with its ordered ingredient list."""
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(404, "Product not found")
    return product


@brands_router.get("", response_model=list[BrandResponse])
def get_brands(
    db: Db,
    _user: CurrentUser,
    q: str | None = Query(None, min_length=1, max_length=200),
    limit: int = Query(50, ge=1, le=200),
) -> list[BrandResponse]:
    """List or search brands."""
    return [
        BrandResponse(id=brand.id, name=brand.name)
        for brand in list_brands(db, q=q, limit=limit)
    ]
