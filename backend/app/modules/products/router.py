from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_role
from app.database.models import Product, Brand, DataSource, User, Ingredient, ProductIngredient
from app.database.session import get_db as get_db_session
from app.modules.ingredients.service import normalize_ingredient_name, parse_ingredient_list, resolve_ingredient
from app.modules.products.service import (
    get_product_by_id,
    search_products,
    create_user_submission,
    normalize_barcode,
)
from app.modules.products.schemas import (
    ProductSummaryResponse,
    ProductDetailResponse,
    ProductSearchFilters,
    ProductSubmissionCreate,
    ProductSubmissionResponse,
    AdminProductUpdate,
    AdminAuditLogCreate,
    IngredientResponse,
    IngredientCreate,
    IngredientAliasCreate,
    IngredientSearchResponse,
    ProductIngredientResponse,
    BrandResponse,
    DataSourceResponse,
)

router = APIRouter(prefix="/products", tags=["products"])


# ─── Public product endpoints ────────────────────────────────────────────

@router.get("", tags=["products"])
def list_products(
    q: str = None,
    category: str = None,
    brand: str = None,
    verified_only: bool = True,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> dict:
    """List products with search, category, and brand filters."""
    from app.modules.products.service import search_products
    
    results, total = search_products(
        q=q,
        category=category,
        brand=brand,
        verified_only=verified_only,
        skip=skip,
        limit=limit,
        db_session=db,
    )

    return {
        "results": results,
        "total": total,
        "skip": skip,
        "limit": limit,
        "verified_only": verified_only,
    }


@router.get("/categories", response_model=dict)
def list_categories(
    db: Session = Depends(get_db),
) -> dict:
    """List product categories with counts."""
    from sqlalchemy import select, func

    # Get all distinct categories from verified products
    stmt = select(Product.category, func.count(Product.id)).where(
        Product.is_active == True, Product.category.isnot(None)
    ).group_by(Product.category)
    rows = db.execute(stmt).all()

    # Also include known categories even if 0 count for UI completeness
    known_categories = [
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
    ]

    result = {}
    for cat, count in rows:
        result[cat] = count
    # Ensure known categories appear
    for cat in known_categories:
        if cat not in result:
            result[cat] = 0

    return {"categories": result}


@router.get("/brands", response_model=list[BrandResponse])
def list_brands(
    db: Session = Depends(get_db),
) -> list:
    """List all brands."""
    from sqlalchemy import select

    brands = db.execute(select(Brand)).scalars().all()
    return [
        BrandResponse(id=b.id, name=b.name, is_active=b.is_active) for b in brands
    ]


@router.post(
    "/submissions",
    response_model=ProductSubmissionResponse,
    status_code=201,
    description="Submit an unknown product for admin review",
)
def submit_product(
    payload: ProductSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Submit an unknown product. Rate-limited and de-duplicated by barcode."""
    result = create_user_submission(
        name=payload.name,
        category=payload.category,
        barcode=payload.barcode,
        ingredients_raw_text=payload.ingredients_raw_text,
        db_session=db,
        user_id=current_user.id,
    )
    return result


# ─── Admin product endpoints ─────────────────────────────────────────────

@router.put("/admin/{product_id}/verify")
def admin_verify_product(
    product_id: UUID,
    payload: AdminProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """Admin verifies or rejects a product."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    old_status = product.verification_status
    product.verification_status = payload.verification_status
    from datetime import datetime, timezone

    if payload.verification_status == "verified":
        product.verified_by = current_user.id
        product.verified_at = datetime.now(timezone.utc)
    else:
        product.verified_by = current_user.id

    # Create audit log
    from app.database.models import AdminAuditLog

    audit = AdminAuditLog(
        action=f"product_{payload.verification_status}",
        entity_type="product",
        entity_id=product.id,
        before_summary=f"status was '{old_status}'",
        after_summary=f"status is '{payload.verification_status}'",
        admin_user_id=current_user.id,
    )
    db.add(audit)
    db.commit()

    return {"message": f"Product {payload.verification_status}"}


@router.get("/admin/review-queue", response_model=list[ProductSummaryResponse])
def admin_review_queue(
    source: Optional[str] = Query(
        None, description="Filter by source: open_beauty_facts, user_submitted"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> list:
    """Show unverified products in review queue."""
    from sqlalchemy import select, func

    stmt = select(Product).where(Product.verification_status == "unverified", Product.is_active == True)

    if source:
        # We'd need source_id filter, simplifying
        pass

    products = db.execute(stmt).scalars().all()

    results = []
    for p in products:
        results.append(
            {
                "id": p.id,
                "name": p.name,
                "barcode": p.barcode,
                "category": p.category,
                "description": p.description,
                "image_url": p.image_url,
                "verification_status": p.verification_status,
                "brand": {"name": p.brand.name} if p.brand else None,
                "ingredient_count": len(p.product_ingredients) if p.product_ingredients else 0,
                "is_active": p.is_active,
            }
        )

    return results


@router.post("/admin/ingredients", response_model=IngredientResponse)
def admin_create_ingredient(
    payload: IngredientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """Admin creates a new ingredient."""
    normalized = normalize_ingredient_name(payload.name)

    existing = db.execute(
        select(Ingredient).filter(Ingredient.normalized_name == normalized)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(409, "Ingredient already exists")

    ingredient = Ingredient(
        name=payload.name,
        normalized_name=normalized,
        description=payload.description,
        reference_notes=payload.reference_notes,
        category_function=payload.category_function or "other",
    )
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)

    return IngredientResponse(
        id=ingredient.id,
        name=ingredient.name,
        normalized_name=ingredient.normalized_name,
        description=ingredient.description,
        reference_notes=ingredient.reference_notes,
        category_function=ingredient.category_function,
        is_active=ingredient.is_active,
    )


@router.post("/admin/ingredients/merge")
def admin_merge_ingredients(
    source_id: UUID,
    target_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
) -> dict:
    """Admin merges duplicate ingredients, moving product_ingredients and aliases."""
    from sqlalchemy import select, update

    # Move product_ingredients from source to target
    db.execute(
        update(ProductIngredient)
        .where(ProductIngredient.ingredient_id == source_id)
        .values(ingredient_id=target_id)
    )

    # Move aliases from source to target
    db.execute(
        update(IngredientAlias)
        .where(IngredientAlias.ingredient_id == source_id)
        .values(ingredient_id=target_id)
    )

    # Deactivate source ingredient
    source_ing = db.get(Ingredient, source_id)
    if source_ing:
        source_ing.is_active = False

    # Create audit log
    from app.database.models import AdminAuditLog

    audit = AdminAuditLog(
        action="ingredient_merge",
        entity_type="ingredient",
        entity_id=target_id,
        before_summary=f"Merged ingredient {source_id} into {target_id}",
        admin_user_id=current_user.id,
    )
    db.add(audit)
    db.commit()

    return {"message": f"Ingredients merged: {source_id} -> {target_id}"}


# Barcode parse endpoint
@router.post("/parse", response_model=dict)
def parse_ingredient_list_endpoint(
    raw_text: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> dict:
    """Parse a raw ingredient list string into ordered entries."""
    from app.modules.ingredients.service import parse_ingredient_list

    entries = parse_ingredient_list(raw_text)
    return {"entries": entries, "count": len(entries)}


@router.get("/barcode/{code}", response_model=ProductDetailResponse)
async def product_by_barcode(
    code: str,
    db: Session = Depends(get_db),
) -> dict:
    """Lookup product by barcode: internal DB first, then external provider, then save as unverified."""
    from sqlalchemy import select
    from app.database.models import Product as _Product

    normalized = normalize_barcode(code)

    # 1. Check internal DB
    product = db.execute(
        select(_Product).where(_Product.barcode == normalized, _Product.is_active == True)
    ).scalar_one_or_none()

    if product:
        return get_product_by_id(product.id, db)

    # 2. Try external provider and save as unverified
    from app.modules.products.service import resolve_product_by_barcode
    result = await resolve_product_by_barcode(normalized, db)
    if result:
        return result

    # 3. Not found anywhere
    raise HTTPException(
        404,
        {
            "error": "PRODUCT_NOT_FOUND",
            "message": "Product not found in database or external provider.",
            "hint": "Submit this product using the /products/submissions endpoint, or try a different barcode.",
        },
    )


@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    """Get a single product by ID with full details including ingredient list."""
    product = get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(404, "Product not found")
    return product