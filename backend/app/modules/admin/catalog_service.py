"""Admin catalogue operations for ingredients."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database.models import Ingredient, IngredientAlias, User
from app.modules.ingredients.schemas import (
    IngredientCreate,
    IngredientUpdate,
)
from app.modules.ingredients.service import (
    merge_ingredients,
    normalize_ingredient_name,
)
from app.modules.products.service import write_audit


def list_ingredients(
    db: Session,
    *,
    q: str | None = None,
    unreviewed_only: bool = False,
    include_inactive: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Ingredient], int]:
    stmt = select(Ingredient)
    count_stmt = select(func.count(Ingredient.id))
    if not include_inactive:
        stmt = stmt.where(Ingredient.is_active.is_(True))
        count_stmt = count_stmt.where(Ingredient.is_active.is_(True))
    if unreviewed_only:
        stmt = stmt.where(Ingredient.is_reviewed.is_(False))
        count_stmt = count_stmt.where(Ingredient.is_reviewed.is_(False))
    if q:
        normalized = normalize_ingredient_name(q)
        pattern = f"%{normalized}%"
        alias_ids = select(IngredientAlias.ingredient_id).where(
            IngredientAlias.alias_normalized.ilike(pattern)
        )
        condition = or_(
            Ingredient.normalized_name.ilike(pattern),
            Ingredient.id.in_(alias_ids),
        )
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)
    total = db.scalar(count_stmt) or 0
    items = list(
        db.scalars(
            stmt.order_by(Ingredient.name.asc()).offset(max(0, offset)).limit(limit)
        ).all()
    )
    return items, total


def create_ingredient(db: Session, *, actor: User, payload: IngredientCreate) -> Ingredient:
    normalized = normalize_ingredient_name(payload.name)
    existing = db.scalar(
        select(Ingredient).where(Ingredient.normalized_name == normalized)
    )
    if existing is not None:
        raise HTTPException(409, "Ingredient already exists")

    ingredient = Ingredient(
        name=payload.name.strip(),
        normalized_name=normalized,
        description=payload.description,
        reference_notes=payload.reference_notes,
        category_function=payload.category_function or "other",
        is_reviewed=payload.is_reviewed,
        is_active=True,
    )
    db.add(ingredient)
    db.flush()
    write_audit(
        db,
        actor=actor,
        action="ingredient_create",
        entity_type="ingredient",
        entity_id=ingredient.id,
        after=ingredient.name,
    )
    db.commit()
    db.refresh(ingredient)
    return ingredient


def update_ingredient(
    db: Session, *, actor: User, ingredient_id: UUID, payload: IngredientUpdate
) -> Ingredient:
    ingredient = db.get(Ingredient, ingredient_id)
    if ingredient is None:
        raise HTTPException(404, "Ingredient not found")

    before = f"{ingredient.name} | reviewed={ingredient.is_reviewed}"
    if payload.name is not None:
        normalized = normalize_ingredient_name(payload.name)
        clash = db.scalar(
            select(Ingredient).where(
                Ingredient.normalized_name == normalized,
                Ingredient.id != ingredient.id,
            )
        )
        if clash is not None:
            raise HTTPException(409, "Another ingredient already uses that normalized name")
        ingredient.name = payload.name.strip()
        ingredient.normalized_name = normalized
    if payload.description is not None:
        ingredient.description = payload.description
    if payload.reference_notes is not None:
        ingredient.reference_notes = payload.reference_notes
    if payload.category_function is not None:
        ingredient.category_function = payload.category_function
    if payload.is_reviewed is not None:
        ingredient.is_reviewed = payload.is_reviewed
    if payload.is_active is not None:
        ingredient.is_active = payload.is_active

    write_audit(
        db,
        actor=actor,
        action="ingredient_update",
        entity_type="ingredient",
        entity_id=ingredient.id,
        before=before,
        after=f"{ingredient.name} | reviewed={ingredient.is_reviewed}",
    )
    db.commit()
    db.refresh(ingredient)
    return ingredient


def add_alias(
    db: Session, *, actor: User, ingredient_id: UUID, alias: str
) -> IngredientAlias:
    ingredient = db.get(Ingredient, ingredient_id)
    if ingredient is None:
        raise HTTPException(404, "Ingredient not found")
    normalized = normalize_ingredient_name(alias)
    if not normalized:
        raise HTTPException(400, "Alias cannot be blank")

    existing = db.scalar(
        select(IngredientAlias).where(IngredientAlias.alias_normalized == normalized)
    )
    if existing is not None:
        raise HTTPException(409, "Alias already exists")

    record = IngredientAlias(ingredient_id=ingredient.id, alias_normalized=normalized)
    db.add(record)
    write_audit(
        db,
        actor=actor,
        action="ingredient_alias_create",
        entity_type="ingredient",
        entity_id=ingredient.id,
        after=f"alias={normalized}",
    )
    db.commit()
    db.refresh(record)
    return record


def merge(
    db: Session,
    *,
    actor: User,
    source_id: UUID,
    target_id: UUID,
) -> dict[str, Any]:
    try:
        result = merge_ingredients(source_id, target_id, db)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from None
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from None

    write_audit(
        db,
        actor=actor,
        action="ingredient_merge",
        entity_type="ingredient",
        entity_id=target_id,
        before=f"source={source_id}",
        after=f"target={target_id}",
    )
    db.commit()
    return result
