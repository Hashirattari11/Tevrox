from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from app.core.deps import get_db
from app.database.models import Ingredient, IngredientAlias
from app.modules.ingredients.service import (
    normalize_ingredient_name,
    parse_ingredient_list,
    resolve_ingredient,
)
from app.modules.ingredients.schemas import (
    IngredientResponse,
    IngredientCreate,
    IngredientUpdate,
    IngredientAliasCreate,
    IngredientSearchResponse,
    ProductIngredientResponse,
)

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.get("/", response_model=List[IngredientSearchResponse])
def list_ingredients(
    q: Optional[str] = Query(None, min_length=1),
    db: Session = Depends(get_db),
) -> list:
    """List ingredients, optionally search by name."""
    query = db.query(Ingredient)
    if q:
        normalized = normalize_ingredient_name(q)
        query = query.filter(
            Ingredient.normalized_name.ilike(f"%{normalized}%")
        )
        # Also check aliases
        query = query.outerjoin(IngredientAlias).filter(
            or_(
                Ingredient.normalized_name.ilike(f"%{normalized}%"),
                IngredientAlias.alias_normalized.ilike(f"%{normalized}%"),
            )
        )
    ingredients = query.distinct().all()
    return [
        IngredientSearchResponse(
            id=ing.id,
            name=ing.name,
            normalized_name=ing.normalized_name,
        )
        for ing in ingredients
    ]


@router.get("/{ingredient_id}", response_model=IngredientResponse)
def get_ingredient(
    ingredient_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    """Get a single ingredient by ID."""
    ing = db.get(Ingredient, ingredient_id)
    if ing is None:
        raise HTTPException(404, "Ingredient not found")
    return IngredientResponse(
        id=ing.id,
        name=ing.name,
        normalized_name=ing.normalized_name,
        description=ing.description,
        reference_notes=ing.reference_notes,
        category_function=ing.category_function,
        is_active=ing.is_active,
    )


@router.post("/", response_model=IngredientResponse, status_code=201)
def create_ingredient(
    payload: IngredientCreate,
    db: Session = Depends(get_db),
) -> dict:
    """Create a new ingredient with normalized name."""
    normalized = normalize_ingredient_name(payload.name)

    # Check if ingredient already exists by normalized name
    existing = db.query(Ingredient).filter(Ingredient.normalized_name == normalized).first()
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


@router.post("/alias", status_code=201)
def create_alias(
    payload: IngredientAliasCreate,
    db: Session = Depends(get_db),
) -> dict:
    """Create an alias for an existing ingredient."""
    normalized = normalize_ingredient_name(payload.alias)

    # Check if alias already exists
    existing = db.query(IngredientAlias).filter(IngredientAlias.alias_normalized == normalized).first()
    if existing:
        raise HTTPException(409, "Alias already exists")

    from app.database.models import Ingredient as _Ingredient

    # Link to an ingredient - for now, we need the ingredient_id
    # In production, this would be specified; for now, just store the alias
    # with a placeholder and let admins associate it later
    alias = IngredientAlias(
        ingredient_id=None,  # Will be associated later
        alias_normalized=normalized,
    )
    db.add(alias)
    db.commit()

    return {"alias": normalized, "note": "Associate with ingredient ID later"}


@router.post("/parse", status_code=200)
def parse_ingredient_list_endpoint(
    raw_text: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> dict:
    """Parse a raw ingredient list string into ordered entries."""
    entries = parse_ingredient_list(raw_text)
    return {"entries": entries, "count": len(entries)}


def or_(**conditions: Any) -> Any:
    """Simple OR condition helper - import from sqlalchemy in real usage."""
    from sqlalchemy import or_ as _or
    return _or(*conditions.values())