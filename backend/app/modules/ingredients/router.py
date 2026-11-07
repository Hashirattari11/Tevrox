from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.models import Ingredient, IngredientAlias, User
from app.database.session import get_db
from app.modules.ingredients.schemas import (
    IngredientResponse,
    IngredientSearchItem,
)
from app.modules.ingredients.service import normalize_ingredient_name

router = APIRouter(prefix="/ingredients", tags=["ingredients"])
Db = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/search", response_model=list[IngredientSearchItem])
def search_ingredients(
    db: Db,
    _user: CurrentUser,
    q: str = Query(..., min_length=1, max_length=300),
    limit: int = Query(20, ge=1, le=100),
) -> list[IngredientSearchItem]:
    """Search ingredients by normalized name or alias."""
    normalized = normalize_ingredient_name(q)
    pattern = f"%{normalized}%"
    stmt = (
        select(Ingredient)
        .outerjoin(IngredientAlias, IngredientAlias.ingredient_id == Ingredient.id)
        .where(
            Ingredient.is_active.is_(True),
            or_(
                Ingredient.normalized_name.ilike(pattern),
                IngredientAlias.alias_normalized.ilike(pattern),
            ),
        )
        .distinct()
        .order_by(Ingredient.name.asc())
        .limit(limit)
    )
    return [
        IngredientSearchItem.model_validate(item) for item in db.scalars(stmt).all()
    ]


@router.get("", response_model=list[IngredientSearchItem])
def list_ingredients(
    db: Db,
    _user: CurrentUser,
    q: str | None = Query(None, min_length=1, max_length=300),
    limit: int = Query(50, ge=1, le=100),
) -> list[IngredientSearchItem]:
    """List active ingredients, optionally filtered by a search term."""
    stmt = select(Ingredient).where(Ingredient.is_active.is_(True))
    if q:
        normalized = normalize_ingredient_name(q)
        stmt = (
            stmt.outerjoin(IngredientAlias, IngredientAlias.ingredient_id == Ingredient.id)
            .where(
                or_(
                    Ingredient.normalized_name.ilike(f"%{normalized}%"),
                    IngredientAlias.alias_normalized.ilike(f"%{normalized}%"),
                )
            )
            .distinct()
        )
    stmt = stmt.order_by(Ingredient.name.asc()).limit(limit)
    return [
        IngredientSearchItem.model_validate(item) for item in db.scalars(stmt).all()
    ]


@router.get("/{ingredient_id}", response_model=IngredientResponse)
def get_ingredient(
    ingredient_id: UUID,
    db: Db,
    _user: CurrentUser,
) -> IngredientResponse:
    """Get a single ingredient by id."""
    ingredient = db.get(Ingredient, ingredient_id)
    if ingredient is None:
        raise HTTPException(404, "Ingredient not found")
    return IngredientResponse.model_validate(ingredient)
