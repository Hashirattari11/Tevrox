"""Product catalogue service: search, details, barcode lookup, submissions, admin."""

from __future__ import annotations

import base64
import re
import threading
import time
from collections import defaultdict, deque
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.database.models import (
    AdminAuditLog,
    Brand,
    DataSource,
    Product,
    ProductIngredient,
    User,
    VerificationStatus,
)
from app.integrations.product_provider import (
    ExternalProductDTO,
    get_product_provider,
)
from app.modules.ingredients.service import (
    link_product_ingredients,
)
from app.modules.products.schemas import (
    AdminProductCreate,
    AdminProductUpdate,
    BrandResponse,
    ProductDetail,
    ProductIngredientDetail,
    ProductListResponse,
    ProductSummary,
    SourceResponse,
)

settings = get_settings()

SOURCE_INTERNAL = "internal_admin"
SOURCE_OPEN_BEAUTY_FACTS = "open_beauty_facts"
SOURCE_USER_SUBMITTED = "user_submitted"

_submission_lock = threading.Lock()
_submission_attempts: dict[str, deque[float]] = defaultdict(deque)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def normalize_barcode(code: str) -> str:
    """Keep digits and enforce the 8-14 digit barcode contract."""
    digits = re.sub(r"\D", "", code or "")
    if not (8 <= len(digits) <= 14):
        raise HTTPException(
            400,
            {
                "code": "INVALID_BARCODE",
                "message": "Barcode must contain 8 to 14 digits.",
            },
        )
    return digits


def encode_cursor(offset: int) -> str:
    return base64.urlsafe_b64encode(str(offset).encode()).decode().rstrip("=")


def decode_cursor(cursor: str | None) -> int:
    if not cursor:
        return 0
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        offset = int(base64.urlsafe_b64decode(padded.encode()).decode())
        return max(0, offset)
    except Exception:
        raise HTTPException(
            400, {"code": "INVALID_CURSOR", "message": "The pagination cursor is invalid."}
        ) from None


def get_or_create_brand(db: Session, name: str | None) -> Brand | None:
    if not name or not name.strip():
        return None
    cleaned = name.strip()[:200]
    brand = db.scalar(select(Brand).where(func.lower(Brand.name) == cleaned.lower()))
    if brand is None:
        brand = Brand(name=cleaned)
        db.add(brand)
        db.flush()
    return brand


def get_source(db: Session, name: str) -> DataSource:
    source = db.scalar(select(DataSource).where(DataSource.name == name))
    if source is None:
        source = DataSource(name=name)
        db.add(source)
        db.flush()
    return source


def write_audit(
    db: Session,
    *,
    actor: User,
    action: str,
    entity_type: str,
    entity_id: UUID | None,
    before: str | None = None,
    after: str | None = None,
) -> None:
    db.add(
        AdminAuditLog(
            admin_user_id=actor.id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_summary=(before or "")[:500] or None,
            after_summary=(after or "")[:500] or None,
        )
    )


def _brand_response(brand: Brand | None) -> BrandResponse | None:
    return BrandResponse(id=brand.id, name=brand.name) if brand else None


def _source_response(source: DataSource | None) -> SourceResponse | None:
    return SourceResponse(id=source.id, name=source.name) if source else None


def serialize_summary(product: Product) -> ProductSummary:
    return ProductSummary(
        id=product.id,
        name=product.name,
        barcode=product.barcode,
        category=product.category,
        description=product.description,
        image_url=product.image_url,
        verification_status=str(product.verification_status),
        brand=_brand_response(product.brand),
        source=_source_response(product.source),
        ingredient_count=len(product.product_ingredients or []),
        is_active=product.is_active,
    )


def serialize_detail(product: Product) -> ProductDetail:
    ordered = sorted(
        product.product_ingredients or [],
        key=lambda item: (item.position is None, item.position if item.position is not None else 0),
    )
    ingredients = [
        ProductIngredientDetail(
            id=link.id,
            product_id=product.id,
            ingredient_id=link.ingredient_id,
            name=link.ingredient.name if link.ingredient else "Unknown ingredient",
            normalized_name=(
                link.ingredient.normalized_name if link.ingredient else "unknown ingredient"
            ),
            position=link.position,
            original_text=link.original_text,
            concentration=link.concentration,
            category_function=link.ingredient.category_function if link.ingredient else None,
            description=link.ingredient.description if link.ingredient else None,
        )
        for link in ordered
    ]
    return ProductDetail(
        id=product.id,
        name=product.name,
        barcode=product.barcode,
        category=product.category,
        description=product.description,
        image_url=product.image_url,
        verification_status=str(product.verification_status),
        brand=_brand_response(product.brand),
        source=_source_response(product.source),
        ingredient_count=len(ingredients),
        is_active=product.is_active,
        verified_by=product.verified_by,
        verified_at=product.verified_at,
        created_by=product.created_by,
        ingredients_raw_text=product.ingredients_raw_text,
        ingredients=ingredients,
    )


def _product_load_options() -> tuple[Any, ...]:
    return (
        selectinload(Product.brand),
        selectinload(Product.source),
        selectinload(Product.product_ingredients).selectinload(ProductIngredient.ingredient),
    )


def get_product_by_id(db: Session, product_id: UUID) -> ProductDetail | None:
    stmt = (
        select(Product)
        .options(*_product_load_options())
        .where(Product.id == product_id, Product.is_active.is_(True))
    )
    product = db.scalar(stmt)
    return serialize_detail(product) if product else None


# ---------------------------------------------------------------------------
# Search and catalog metadata
# ---------------------------------------------------------------------------


def search_products(
    db: Session,
    *,
    q: str | None = None,
    category: str | None = None,
    brand: str | None = None,
    verified_only: bool = True,
    limit: int = 20,
    cursor: str | None = None,
    offset: int | None = None,
) -> ProductListResponse:
    start = max(0, offset) if offset is not None else decode_cursor(cursor)
    limit = max(1, min(limit, 100))

    stmt = (
        select(Product)
        .join(Brand, Product.brand_id == Brand.id, isouter=True)
        .options(*_product_load_options())
        .where(Product.is_active.is_(True))
    )
    count_stmt = (
        select(func.count(func.distinct(Product.id)))
        .select_from(Product)
        .join(Brand, Product.brand_id == Brand.id, isouter=True)
        .where(Product.is_active.is_(True))
    )

    if q:
        term = f"%{q.strip()}%"
        condition = or_(Product.name.ilike(term), Brand.name.ilike(term))
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)
    if category:
        category_value = category.strip().lower().replace(" ", "_").replace("-", "_")
        stmt = stmt.where(Product.category == category_value)
        count_stmt = count_stmt.where(Product.category == category_value)
    if brand:
        term = f"%{brand.strip()}%"
        stmt = stmt.where(Brand.name.ilike(term))
        count_stmt = count_stmt.where(Brand.name.ilike(term))
    if verified_only:
        stmt = stmt.where(Product.verification_status == VerificationStatus.verified)
        count_stmt = count_stmt.where(Product.verification_status == VerificationStatus.verified)

    total = db.scalar(count_stmt) or 0
    products = db.scalars(
        stmt.order_by(Product.name.asc(), Product.id.asc()).offset(start).limit(limit)
    ).all()
    next_offset = start + limit
    return ProductListResponse(
        items=[serialize_summary(item) for item in products],
        total=total,
        limit=limit,
        next_cursor=encode_cursor(next_offset) if next_offset < total else None,
        verified_only=verified_only,
    )


def list_categories(db: Session) -> list[dict[str, Any]]:
    rows = db.execute(
        select(Product.category, func.count(Product.id))
        .where(Product.is_active.is_(True))
        .group_by(Product.category)
    ).all()
    counts = {category: count for category, count in rows if category}
    from app.modules.products.schemas import PRODUCT_CATEGORIES

    return [
        {"category": category, "count": int(counts.get(category, 0))}
        for category in PRODUCT_CATEGORIES
    ]


def list_brands(db: Session, q: str | None = None, limit: int = 50) -> list[Brand]:
    stmt = select(Brand).order_by(Brand.name.asc()).limit(max(1, min(limit, 200)))
    if q:
        stmt = stmt.where(Brand.name.ilike(f"%{q.strip()}%"))
    return list(db.scalars(stmt).all())


# ---------------------------------------------------------------------------
# Barcode lookup
# ---------------------------------------------------------------------------


async def lookup_barcode(db: Session, code: str) -> ProductDetail:
    """Internal DB first, then external provider, then store as unverified."""
    barcode = normalize_barcode(code)

    product = db.scalar(
        select(Product)
        .options(*_product_load_options())
        .where(Product.barcode == barcode, Product.is_active.is_(True))
    )
    if product is not None:
        return serialize_detail(product)

    try:
        external = await get_product_provider().lookup_by_barcode(barcode)
    except Exception:
        # Providers are best-effort: never turn a provider failure into a 500.
        external = None

    if external is None:
        raise HTTPException(
            404,
            {
                "code": "PRODUCT_NOT_FOUND",
                "message": "Product not found in the Tevrox catalogue or the external provider.",
                "hint": (
                    "Use POST /api/v1/products/submissions (or the Add product screen) "
                    "to submit this product for admin review."
                ),
            },
        )

    created = _save_external_product(db, barcode, external)
    return serialize_detail(created)


def _save_external_product(
    db: Session, barcode: str, external: ExternalProductDTO
) -> Product:
    name = external.display_name
    if not name:
        raise HTTPException(
            404,
            {
                "code": "PRODUCT_NOT_FOUND",
                "message": "The external provider returned an incomplete product record.",
                "hint": "Submit this product manually so an admin can review it.",
            },
        )

    brand = get_or_create_brand(db, external.brand)
    source = get_source(db, SOURCE_OPEN_BEAUTY_FACTS)
    product = Product(
        name=name,
        barcode=barcode,
        category=external.category,
        description=name,
        image_url=external.image_url,
        external_id=barcode,
        source_id=source.id,
        brand_id=brand.id if brand else None,
        verification_status=VerificationStatus.unverified,
        is_active=True,
    )
    db.add(product)
    db.flush()
    link_product_ingredients(product, external.ingredients_text, db)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(
            select(Product)
            .options(*_product_load_options())
            .where(Product.barcode == barcode, Product.is_active.is_(True))
        )
        if existing is not None:
            return existing
        raise
    db.refresh(product)
    return product


# ---------------------------------------------------------------------------
# User submissions
# ---------------------------------------------------------------------------


def _enforce_submission_rate_limit(user_id: UUID) -> None:
    now = time.monotonic()
    window = settings.product_submission_rate_window_seconds
    limit = settings.product_submission_rate_limit
    key = str(user_id)
    with _submission_lock:
        attempts = _submission_attempts[key]
        while attempts and attempts[0] <= now - window:
            attempts.popleft()
        if len(attempts) >= limit:
            raise HTTPException(
                429,
                {
                    "code": "RATE_LIMITED",
                    "message": "Too many product submissions. Please try again later.",
                },
            )
        attempts.append(now)


def clear_submission_rate_limits() -> None:
    """Test helper: reset the in-memory submission rate limiter."""
    with _submission_lock:
        _submission_attempts.clear()


def create_user_submission(
    db: Session,
    *,
    user: User,
    name: str,
    category: str,
    barcode: str | None,
    brand_name: str | None,
    ingredients_raw_text: str,
) -> Product:
    _enforce_submission_rate_limit(user.id)

    normalized_barcode = normalize_barcode(barcode) if barcode else None
    if normalized_barcode:
        existing = db.scalar(
            select(Product).where(
                Product.barcode == normalized_barcode, Product.is_active.is_(True)
            )
        )
        if existing is not None:
            raise HTTPException(
                409,
                {
                    "code": "PRODUCT_ALREADY_EXISTS",
                    "message": "A product with this barcode already exists in the catalogue.",
                },
            )

    brand = get_or_create_brand(db, brand_name)
    source = get_source(db, SOURCE_USER_SUBMITTED)
    product = Product(
        name=name.strip(),
        barcode=normalized_barcode,
        category=category,
        description=f"User-submitted product: {name.strip()}",
        source_id=source.id,
        brand_id=brand.id if brand else None,
        verification_status=VerificationStatus.unverified,
        created_by=user.id,
        is_active=True,
    )
    db.add(product)
    db.flush()
    link_product_ingredients(product, ingredients_raw_text, db)
    db.commit()
    db.refresh(product)
    return product


# ---------------------------------------------------------------------------
# Admin product management
# ---------------------------------------------------------------------------


def _ensure_barcode_available(
    db: Session, barcode: str | None, *, exclude_id: UUID | None = None
) -> None:
    if not barcode:
        return
    stmt = select(Product).where(Product.barcode == barcode)
    if exclude_id is not None:
        stmt = stmt.where(Product.id != exclude_id)
    if db.scalar(stmt) is not None:
        raise HTTPException(
            409,
            {
                "code": "PRODUCT_ALREADY_EXISTS",
                "message": "A product with this barcode already exists.",
            },
        )


def admin_create_product(
    db: Session, *, actor: User, payload: AdminProductCreate
) -> ProductDetail:
    barcode = normalize_barcode(payload.barcode) if payload.barcode else None
    _ensure_barcode_available(db, barcode)

    brand = get_or_create_brand(db, payload.brand_name)
    source = get_source(db, SOURCE_INTERNAL)
    product = Product(
        name=payload.name.strip(),
        barcode=barcode,
        category=payload.category,
        description=payload.description,
        image_url=payload.image_url,
        source_id=source.id,
        brand_id=brand.id if brand else None,
        verification_status=VerificationStatus(payload.verification_status),
        verified_by=actor.id if payload.verification_status == "verified" else None,
        verified_at=(
            datetime.now(UTC) if payload.verification_status == "verified" else None
        ),
        created_by=actor.id,
        is_active=True,
    )
    db.add(product)
    db.flush()
    if payload.ingredients_raw_text:
        link_product_ingredients(product, payload.ingredients_raw_text, db)
    write_audit(
        db,
        actor=actor,
        action="product_create",
        entity_type="product",
        entity_id=product.id,
        after=f"{product.name} ({product.verification_status})",
    )
    db.commit()
    detail = get_product_by_id(db, product.id)
    assert detail is not None
    return detail


def admin_update_product(
    db: Session, *, actor: User, product_id: UUID, payload: AdminProductUpdate
) -> ProductDetail:
    product = db.scalar(
        select(Product).options(*_product_load_options()).where(Product.id == product_id)
    )
    if product is None:
        raise HTTPException(404, "Product not found")

    before = f"{product.name} | {product.category} | {product.verification_status}"
    barcode = normalize_barcode(payload.barcode) if payload.barcode else None
    if payload.barcode is not None:
        _ensure_barcode_available(db, barcode, exclude_id=product.id)
        product.barcode = barcode

    if payload.name is not None:
        product.name = payload.name.strip()
    if payload.category is not None:
        product.category = payload.category
    if payload.description is not None:
        product.description = payload.description
    if payload.image_url is not None:
        product.image_url = payload.image_url
    if payload.brand_name is not None:
        brand = get_or_create_brand(db, payload.brand_name)
        product.brand_id = brand.id if brand else None
    if payload.ingredients_raw_text is not None:
        for link in list(product.product_ingredients):
            db.delete(link)
        db.flush()
        db.expire(product, ["product_ingredients"])
        link_product_ingredients(product, payload.ingredients_raw_text, db)

    write_audit(
        db,
        actor=actor,
        action="product_update",
        entity_type="product",
        entity_id=product.id,
        before=before,
        after=f"{product.name} | {product.category} | {product.verification_status}",
    )
    db.commit()
    detail = get_product_by_id(db, product.id)
    assert detail is not None
    return detail


def admin_soft_delete(db: Session, *, actor: User, product_id: UUID) -> None:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(404, "Product not found")
    product.is_active = False
    write_audit(
        db,
        actor=actor,
        action="product_soft_delete",
        entity_type="product",
        entity_id=product.id,
        before="is_active=True",
        after="is_active=False",
    )
    db.commit()


def admin_set_verification(
    db: Session,
    *,
    actor: User,
    product_id: UUID,
    status: str,
    reason: str | None = None,
) -> ProductDetail:
    if status not in {"verified", "rejected"}:
        raise HTTPException(400, "Verification status must be 'verified' or 'rejected'")
    product = db.scalar(
        select(Product).options(*_product_load_options()).where(Product.id == product_id)
    )
    if product is None:
        raise HTTPException(404, "Product not found")

    before = str(product.verification_status)
    product.verification_status = VerificationStatus(status)
    product.verified_by = actor.id
    product.verified_at = datetime.now(UTC)
    write_audit(
        db,
        actor=actor,
        action=f"product_{status}",
        entity_type="product",
        entity_id=product.id,
        before=f"status={before}",
        after=f"status={status}" + (f"; reason={reason}" if reason else ""),
    )
    db.commit()
    detail = get_product_by_id(db, product.id)
    assert detail is not None
    return detail


def admin_review_queue(
    db: Session, *, source_name: str | None = None
) -> list[ProductSummary]:
    stmt = (
        select(Product)
        .options(*_product_load_options())
        .join(DataSource, Product.source_id == DataSource.id, isouter=True)
        .where(
            Product.verification_status == VerificationStatus.unverified,
            Product.is_active.is_(True),
        )
        .order_by(Product.created_at.asc())
    )
    if source_name:
        stmt = stmt.where(DataSource.name == source_name)
    return [serialize_summary(item) for item in db.scalars(stmt).all()]


def admin_list_products(
    db: Session,
    *,
    verified_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> ProductListResponse:
    return search_products(
        db,
        verified_only=verified_only,
        limit=limit,
        offset=offset,
    )
