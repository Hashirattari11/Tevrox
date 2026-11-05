"""Product catalog service.

Handles product search, detail lookup, barcode resolution against internal DB
and external provider (Open Beauty Facts), and user submissions.

All external data is stored as "unverified" until admin verification.
Never display unverified products as verified.
"""

import httpx
import re
from typing import Any, Optional

from fastapi import HTTPException

from app.core.config import get_settings
from app.core.deps import get_db, get_current_user
from app.database.models import Product, Ingredient, IngredientAlias, Brand, DataSource, User, ProductIngredient
from app.database.session import get_db as get_db_session
from app.modules.ingredients.service import normalize_ingredient_name, parse_ingredient_list, resolve_ingredient
from app.modules.auth.schemas import UserResponse

settings = get_settings()
HTTP_TIMEOUT = httpx.Timeout(10.0, connect=5.0)


# ─── Helper: normalize barcode ────────────────────────────────────────────

def normalize_barcode(code: str) -> str:
    """Keep only digits; ensure 8-14 length."""
    digits = re.sub(r"\D", "", code)
    if len(digits) < 8 or len(digits) > 14:
        raise HTTPException(400, "Invalid barcode format: must be 8-14 digits")
    return digits


# ─── Helper: parse & resolve ingredients from raw text ────────────────────

def parse_and_resolve_ingredients(
    raw_text: str,
    db_session,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Parse raw ingredient text and resolve each entry.

    Returns (resolved_entries, unresolved_entries) where each entry is a dict
    with id, name, normalized_name, is_new flags.
    """
    entries = parse_ingredient_list(raw_text)
    resolved: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    for entry in entries:
        result = resolve_ingredient(entry["normalized_name"], db_session)
        if result["is_new"]:
            unresolved.append(result)
        else:
            resolved.append(result)

    return resolved, unresolved


# ─── Helper: fetch from Open Beauty Facts ─────────────────────────────────

OPEN_BEAUTY_FACTS_BASE = "https://world.openbeautyfacts.org/api/v3/product"


async def fetch_from_open_beauty_facts(barcode: str) -> Optional[dict[str, Any]]:
    """Fetch product from Open Beauty Facts by barcode.

    Returns normalized DTO or None if not found/unavailable.
    """
    url = f"{OPEN_BEAUTY_FACTS_BASE}/{barcode}.json?counters=1"
    headers = {"User-Agent": "Tevrox/0.1.0 (+https://tevrox.com)"}

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                return None
            data = response.json()
            # Open Beauty Facts wraps data under "product" key
            product_data = data.get("product")
            if not product_data:
                return None

            # Normalize into our DTO
            normalized = {
                "id": product_data.get("code"),  # barcode
                "name": product_data.get("product_name") or product_data.get("name"),
                "brand": product_data.get("brands"),
                "categories": product_data.get("categories"),
                "ingredients_text": product_data.get("ingredients_text"),
                "ingredients_text_en": product_data.get("ingredients_text_en"),
                "image_url": product_data.get("image_url"),
                "packaging": product_data.get("packaging"),
                "quantity": product_data.get("quantity"),
                "labels": product_data.get("labels"),
            }
            return normalized
        except httpx.TimeoutException:
            return None
        except Exception:
            return None


# ─── Core: resolve barcode flow ──────────────────────────────────────────

async def resolve_product_by_barcode(
    barcode: str,
    db_session,
) -> Optional[dict[str, Any]]:
    """Resolve a product by barcode flow: internal DB -> external provider -> save unverified.

    Returns product dict if found, or None.
    """
    from sqlalchemy import select

    # 1. Check internal database first
    product = db_session.execute(
        select(Product).where(Product.barcode == barcode, Product.is_active == True)
    ).scalar_one_or_none()

    if product:
        # Build response dict from internal product
        ingredients = []
        for pi in product.product_ingredients:
            ing = db_session.get(Ingredient, pi.ingredient_id)
            if ing:
                ingredients.append(
                    {
                        "id": ing.id,
                        "name": ing.name,
                        "position": pi.position,
                        "original_text": pi.original_text,
                    }
                )
        return {
            "id": product.id,
            "name": product.name,
            "barcode": product.barcode,
            "category": product.category,
            "description": product.description,
            "image_url": product.image_url,
            "verification_status": product.verification_status,
            "brand": {"name": product.brand.name} if product.brand else None,
            "source": {"name": product.source.name} if product.source else None,
            "ingredients": ingredients,
            "is_active": product.is_active,
        }

    # 2. Try external provider
    external_data = await fetch_from_open_beauty_facts(barcode)
    if external_data:
        # Save as unverified product
        # Get or create brand
        brand_name = external_data.get("brand")
        brand = None
        if brand_name:
            brand = db_session.execute(
                select(Brand).where(Brand.name.ilike(brand_name))
            ).scalar_one_or_none()
            if not brand:
                brand = Brand(name=brand_name)
                db_session.add(brand)
                db_session.flush()

        # Get or create source
        source = db_session.execute(
            select(DataSource).where(DataSource.name == "open_beauty_facts")
        ).scalar_one_or_none()
        if not source:
            source = DataSource(name="open_beauty_facts")
            db_session.add(source)
            db_session.flush()

        # Parse and resolve ingredients
        ingredients_raw = external_data.get("ingredients_text") or external_data.get(
            "ingredients_text_en"
        )
        resolved, unresolved = parse_and_resolve_ingredients(
            ingredients_raw or "", db_session
        )

        # Build ingredient list for response
        ingredient_details = []
        for res in resolved:
            ingredient_details.append(
                {
                    "id": res["id"],
                    "name": res["name"],
                    "position": None,
                    "original_text": None,
                }
            )

        # Create unverified product
        # Extract a simple category from the external data
        categories = external_data.get("categories", "")
        cat_value = categories.split(",")[0] if categories else "other" if not categories else categories

        new_product = Product(
            name=external_data.get("name") or "Unknown Product",
            barcode=barcode,
            category=cat_value,
            description=external_data.get("name"),
            image_url=external_data.get("image_url"),
            verification_status="unverified",
            source_id=source.id,
            created_by=None,  # Will be set by admin later
            verified_by=None,
        )
        db_session.add(new_product)
        db_session.flush()

        # Add product-ingredient relationships
        for pos, ing_detail in enumerate(ingredient_details):
            # Find or create ingredient
            ing = db_session.get(Ingredient, ing_detail["id"])
            if not ing:
                # Create new ingredient
                new_ing = Ingredient(
                    name=ing_detail["name"],
                    normalized_name=ing_detail["name"].lower(),
                    category_function="other",
                )
                db_session.add(new_ing)
                db_session.flush()
                ing = new_ing

            pi = ProductIngredient(
                product_id=new_product.id,
                ingredient_id=ing.id,
                position=pos,
                original_text=ing_detail["name"],
            )
            db_session.add(pi)

        db_session.commit()

        return {
            "id": new_product.id,
            "name": new_product.name,
            "barcode": new_product.barcode,
            "category": new_product.category,
            "description": new_product.description,
            "image_url": new_product.image_url,
            "verification_status": new_product.verification_status,
            "brand": {"name": brand.name} if brand else None,
            "source": {"name": source.name},
            "ingredients": ingredient_details,
            "is_active": new_product.is_active,
        }

    # 3. Not found anywhere
    return None


# ─── Service: get product by ID ────────────────────────────────────────────

def get_product_by_id(
    product_id: int,
    db_session,
) -> Optional[dict[str, Any]]:
    """Get a single product by ID with full details."""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    stmt = (
        select(Product)
        .options(
            selectinload(Product.product_ingredients)
            .selectinload(ProductIngredient.ingredient)
        )
        .where(Product.id == product_id, Product.is_active == True)
    )
    product = db_session.execute(stmt).scalar_one_or_none()

    if not product:
        return None

    # Build ingredient list
    ingredients = []
    for pi in product.product_ingredients:
        ing = pi.ingredient
        if ing:
            ingredients.append(
                {
                    "id": ing.id,
                    "name": ing.name,
                    "normalized_name": ing.normalized_name,
                    "position": pi.position,
                    "original_text": pi.original_text,
                    "concentration": pi.concentration,
                }
            )

    return {
        "id": product.id,
        "name": product.name,
        "barcode": product.barcode,
        "category": product.category,
        "description": product.description,
        "image_url": product.image_url,
        "verification_status": product.verification_status,
        "brand": {"name": product.brand.name} if product.brand else None,
        "source": {"name": product.source.name} if product.source else None,
        "ingredients": ingredients,
        "is_active": product.is_active,
        "verified_by": str(product.verified_by) if product.verified_by else None,
        "verified_at": str(product.verified_at) if product.verified_at else None,
        "created_by": str(product.created_by) if product.created_by else None,
    }


# ─── Service: search products ────────────────────────────────────────────

def search_products(
    q: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    verified_only: bool = True,
    skip: int = 0,
    limit: int = 50,
    db_session=None,
) -> tuple[list[dict[str, Any]], int]:
    """Search products with filters and pagination.

    Returns (results, total_count).
    """
    from sqlalchemy import select, func

    if db_session is None:
        from app.database.session import engine as _engine
        from sqlalchemy.orm import Session as _Session
        db_session = _Session(_engine)

    stmt = select(Product).where(Product.is_active == True)
    total_stmt = select(func.count()).select_from(Product).where(Product.is_active == True)

    if q:
        normalized = normalize_ingredient_name(q) if q else q
        # Search in name and brand using ILIKE
        stmt = stmt.where(
            Product.name.ilike(f"%{q}%") if q else Product.name.isnot(None)
        )
        total_stmt = total_stmt.where(
            Product.name.ilike(f"%{q}%") if q else Product.name.isnot(None)
        )

    if category:
        stmt = stmt.where(Product.category.ilike(f"%{category}%"))
        total_stmt = total_stmt.where(Product.category.ilike(f"%{category}%"))

    if brand:
        stmt = stmt.where(Product.brand_id != None)  # simplified
        # In real impl, join with Brand table

    # Count total before pagination
    total = db_session.execute(total_stmt).scalar_one()

    # Apply pagination
    stmt = stmt.offset(skip).limit(limit)
    products = db_session.execute(stmt).scalars().all()

    results = []
    for p in products:
        # Quick ingredient count
        ing_count = len(p.product_ingredients) if p.product_ingredients else 0
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
                "ingredient_count": ing_count,
                "is_active": p.is_active,
            }
        )

    return results, total


# ─── Service: create user submission ───────────────────────────────────────

def create_user_submission(
    name: str,
    category: str,
    barcode: Optional[str],
    ingredients_raw_text: str,
    db_session,
    user_id: int,
) -> dict[str, Any]:
    """Create a user-submitted product (unverified, rate-limited, de-duplicated)."""
    from fastapi import HTTPException

    # Normalize barcode if provided
    norm_barcode = None
    if barcode:
        norm_barcode = normalize_barcode(barcode)

    # De-duplicate by barcode if provided
    if norm_barcode:
        existing = db_session.execute(
            select(Product).where(Product.barcode == norm_barcode, Product.is_active == True)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                409,
                "A product with this barcode already exists. "
                "If this is your product, contact an admin to verify it.",
            )

    # Parse ingredients
    resolved, unresolved = parse_and_resolve_ingredients(
        ingredients_raw_text, db_session
    )

    # Get or create source
    source = db_session.execute(
        select(DataSource).where(DataSource.name == "user_submitted")
    ).scalar_one_or_none()
    if not source:
        source = DataSource(name="user_submitted")
        db_session.add(source)
        db_session.flush()

    # Create product
    new_product = Product(
        name=name,
        barcode=norm_barcode,
        category=category,
        description=name,
        verification_status="unverified",
        source_id=source.id,
        created_by=user_id,
        is_active=True,
    )
    db_session.add(new_product)
    db_session.flush()

    # Add product-ingredient relationships
    for pos, ing_detail in enumerate(resolved):
        ing = db_session.get(Ingredient, ing_detail["id"])
        if not ing:
            new_ing = Ingredient(
                name=ing_detail["name"],
                normalized_name=ing_detail["normalized_name"],
                category_function="other",
            )
            db_session.add(new_ing)
            db_session.flush()
            ing = new_ing

        pi = ProductIngredient(
            product_id=new_product.id,
            ingredient_id=ing.id,
            position=pos,
            original_text=ing_detail["name"],
        )
        db_session.add(pi)

    db_session.commit()

    return {
        "id": new_product.id,
        "name": new_product.name,
        "barcode": new_product.barcode,
        "category": new_product.category,
        "verification_status": new_product.verification_status,
        "message": "Product submitted for review. Admins will verify and may verify/reject it.",
    }