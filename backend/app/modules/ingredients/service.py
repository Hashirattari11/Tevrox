"""Ingredient normalization, parsing, resolution, and merge helpers."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

_PERCENT_IN_BRACKETS = re.compile(r"[\(\[]\s*\d+(?:[.,]\d+)?\s*%\s*[\)\]]")
_PERCENT = re.compile(r"\b\d+(?:[.,]\d+)?\s*%")
_SLASH = re.compile(r"\s*/\s*")
_WHITESPACE = re.compile(r"\s+")
_PREFIX = re.compile(
    r"^\s*(?:ingredients?|inci|composition|ingr[ée]dients?)\s*[:\-\u2013\u2014]\s*",
    flags=re.IGNORECASE,
)
_TRAILING_PUNCTUATION = " \t\r\n.,;:*†‡"


def normalize_ingredient_name(name: str | None) -> str:
    """Normalize an ingredient label for matching.

    The function deliberately keeps meaningful parenthetical text such as
    ``Retinol (Vitamin A)`` while removing percentage annotations, trailing
    punctuation, unicode differences, and inconsistent slash spacing.
    """
    if not name:
        return ""
    text = unicodedata.normalize("NFKC", str(name))
    text = text.strip().lower()
    text = _PERCENT_IN_BRACKETS.sub(" ", text)
    text = _PERCENT.sub(" ", text)
    text = _SLASH.sub(" / ", text)
    text = _WHITESPACE.sub(" ", text)
    text = text.strip(_TRAILING_PUNCTUATION)
    # Tidy spaces that may be left around brackets after removing percentages.
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = _WHITESPACE.sub(" ", text)
    return text.strip()


def _split_top_level(text: str) -> list[str]:
    """Split on commas/semicolons that are not inside brackets."""
    entries: list[str] = []
    current: list[str] = []
    depth = 0
    for char in text:
        if char in "([{":
            depth += 1
            current.append(char)
        elif char in ")]}":
            depth = max(0, depth - 1)
            current.append(char)
        elif char in ",;" and depth == 0:
            segment = "".join(current).strip()
            if segment:
                entries.append(segment)
            current = []
        else:
            current.append(char)
    segment = "".join(current).strip()
    if segment:
        entries.append(segment)
    return entries


def parse_ingredient_list(raw_text: str | None) -> list[dict[str, Any]]:
    """Parse a raw label into ordered ``{"raw", "normalized"}`` entries.

    Handles ``Ingredients:``/``INCI:`` prefixes, newlines, semicolons, commas
    inside parentheses, trailing periods, bullet characters, and messy spacing.
    Empty entries are dropped; duplicate entries are preserved here so callers
    can still inspect the original label order.
    """
    if not raw_text:
        return []

    text = unicodedata.normalize("NFKC", str(raw_text)).strip()
    if not text:
        return []

    text = _PREFIX.sub("", text)
    # Newlines and bullets separate entries just like commas on most labels.
    text = re.sub(r"[\r\n]+", ", ", text)
    text = re.sub(r"(?:^|,\s*)[\u2022\u00b7\u25cf\u25aa\-]\s*", ", ", text)
    # A trailing period ends the list rather than naming an ingredient.
    text = text.rstrip(" .")

    result: list[dict[str, Any]] = []
    for entry in _split_top_level(text):
        raw = entry.strip(" \t.,;:*†‡")
        normalized = normalize_ingredient_name(raw)
        if normalized:
            result.append({"raw": raw, "normalized": normalized})
    return result


def resolve_ingredient(
    name_or_normalized: str,
    db: Session,
    *,
    create: bool = True,
) -> dict[str, Any]:
    """Resolve a name by normalized name or alias.

    Unknown ingredients are created with ``is_reviewed=False`` so admins can
    review them later. The caller owns the transaction; this helper only
    flushes so newly created rows receive an id.
    """
    from app.database.models import Ingredient, IngredientAlias

    normalized = normalize_ingredient_name(name_or_normalized)
    if not normalized:
        raise ValueError("Ingredient name cannot be empty")

    ingredient = db.scalar(
        select(Ingredient).where(
            Ingredient.normalized_name == normalized,
            Ingredient.is_active.is_(True),
        )
    )
    if ingredient is not None:
        return {
            "id": ingredient.id,
            "name": ingredient.name,
            "normalized_name": ingredient.normalized_name,
            "is_new": False,
            "is_reviewed": ingredient.is_reviewed,
        }

    alias = db.scalar(
        select(IngredientAlias).where(IngredientAlias.alias_normalized == normalized)
    )
    if alias is not None:
        linked = db.get(Ingredient, alias.ingredient_id)
        if linked is not None and linked.is_active:
            return {
                "id": linked.id,
                "name": linked.name,
                "normalized_name": linked.normalized_name,
                "is_new": False,
                "is_reviewed": linked.is_reviewed,
            }

    if not create:
        return {
            "id": None,
            "name": name_or_normalized.strip(),
            "normalized_name": normalized,
            "is_new": True,
            "is_reviewed": False,
        }

    new_ingredient = Ingredient(
        name=name_or_normalized.strip() or normalized,
        normalized_name=normalized,
        category_function="other",
        is_reviewed=False,
        is_active=True,
    )
    db.add(new_ingredient)
    db.flush()
    return {
        "id": new_ingredient.id,
        "name": new_ingredient.name,
        "normalized_name": new_ingredient.normalized_name,
        "is_new": True,
        "is_reviewed": False,
    }


def link_product_ingredients(
    product: Any,
    raw_text: str | None,
    db: Session,
) -> list[dict[str, Any]]:
    """Parse and attach every ingredient in ``raw_text`` to ``product``.

    No ingredient is silently dropped. Duplicate normalized names are collapsed
    to one join row (the database enforces one row per product/ingredient), but
    the first label position is kept.
    """
    from app.database.models import ProductIngredient

    entries = parse_ingredient_list(raw_text)
    linked: list[dict[str, Any]] = []
    seen: set[Any] = set()

    for position, entry in enumerate(entries):
        resolved = resolve_ingredient(entry["normalized"], db)
        ingredient_id = resolved["id"]
        if ingredient_id is None or ingredient_id in seen:
            continue
        seen.add(ingredient_id)
        join = ProductIngredient(
            product_id=product.id,
            ingredient_id=ingredient_id,
            position=position,
            original_text=entry["raw"][:500],
        )
        db.add(join)
        linked.append(
            {
                "ingredient_id": ingredient_id,
                "name": resolved["name"],
                "normalized_name": resolved["normalized_name"],
                "position": position,
                "original_text": entry["raw"][:500],
                "is_new": resolved["is_new"],
            }
        )

    product.ingredients_raw_text = raw_text
    return linked


def merge_ingredients(source_id: Any, target_id: Any, db: Session) -> dict[str, Any]:
    """Merge ``source_id`` into ``target_id`` and return movement counts."""
    from app.database.models import Ingredient, IngredientAlias, ProductIngredient

    if source_id == target_id:
        raise ValueError("Cannot merge an ingredient into itself")

    source = db.get(Ingredient, source_id)
    target = db.get(Ingredient, target_id)
    if source is None or target is None:
        raise LookupError("Ingredient not found")

    moved_links = 0
    dropped_links = 0
    for link in list(source.product_ingredients):
        duplicate = db.scalar(
            select(ProductIngredient).where(
                ProductIngredient.product_id == link.product_id,
                ProductIngredient.ingredient_id == target.id,
            )
        )
        if duplicate is not None:
            db.delete(link)
            dropped_links += 1
        else:
            link.ingredient_id = target.id
            moved_links += 1

    moved_aliases = 0
    for alias in list(source.aliases):
        # alias_normalized is globally unique, so any *other* row with the same
        # normalized value belongs to another ingredient; drop the merge side.
        existing = db.scalar(
            select(IngredientAlias).where(
                IngredientAlias.alias_normalized == alias.alias_normalized,
                IngredientAlias.id != alias.id,
            )
        )
        if existing is not None:
            db.delete(alias)
        else:
            alias.ingredient_id = target.id
            moved_aliases += 1

    source.is_active = False
    source.is_reviewed = True
    target.is_reviewed = True
    db.flush()

    return {
        "source_id": source.id,
        "target_id": target.id,
        "moved_product_ingredients": moved_links,
        "dropped_duplicate_links": dropped_links,
        "moved_aliases": moved_aliases,
    }
