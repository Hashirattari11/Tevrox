"""Ingredient normalization, parsing, and resolution logic.

Pure functions with no database dependencies (except resolve_ingredient which
optionally queries the DB). These are the core building blocks for the
product module's barcode lookup and user submission flows.
"""

import re
from typing import Any, Optional

from sqlalchemy.orm import Session


def normalize_ingredient_name(name: str) -> str:
    """Normalize an ingredient name for database lookup.

    Steps:
    - Trim whitespace
    - Lowercase
    - Collapse runs of whitespace to single space
    - Remove bracketed percentages e.g. (10%), [5%]
    - Strip trailing punctuation
    - Unify unicode NFC form (best-effort via lower()+strip)
    - Handle common "Aqua / Water" style slashes by normalizing spaces

    Real-world examples:
        "Aqua / Water"       -> "aqua / water"
        "Niacinamide 10%"   -> "niacinamide"
        "Retinol (Vitamin A)" -> "retinol"
        "  Hyaluronic Acid " -> "hyaluronic acid"
    """
    if not name:
        return ""
    # Decode any URL/%20 style spaces
    s = name
    # Normalize: strip, lowercase
    s = s.strip().lower()
    # Remove bracketed percentages like (10%) or [5%]
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"\[.*?\]", "", s)
    # Remove trailing punctuation (periods, commas)
    s = s.rstrip(".,;:")
    # Collapse any run of whitespace to single space
    s = re.sub(r"\s+", " ", s)
    # Handle slash-separated names: "aqua / water" -> keep as-is (space-padded)
    # but ensure single spacing
    s = re.sub(r"\s+/+\s*", " / ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def parse_ingredient_list(raw_text: str) -> list[dict[str, Any]]:
    """Parse a raw ingredient list string into ordered entries.

    Handles:
    - Commas inside parentheses e.g. "Water (and) Glycerin"
    - Line breaks
    - "Ingredients:" prefix
    - Trailing periods
    - Multiple spaces/tabs

    Returns a list of dicts with 'raw' and 'normalized' keys.
    """
    if not raw_text:
        return []

    text = raw_text.strip()
    # Remove "Ingredients:" prefix (case-insensitive, with optional colon)
    text = re.sub(r"^ingredients?:\s*", "", text, flags=re.IGNORECASE)
    # Remove trailing periods
    text = text.rstrip(".")
    # Replace commas followed by whitespace with a marker that can be inside parens
    # Strategy: split on commas that are NOT inside parentheses
    entries: list[str] = []
    current = []
    paren_depth = 0
    for ch in text:
        if ch == "(":
            paren_depth += 1
            current.append(ch)
        elif ch == ")":
            paren_depth = max(0, paren_depth - 1)
            current.append(ch)
        elif ch == "," and paren_depth == 0:
            segment = "".join(current).strip()
            if segment:
                entries.append(segment)
            current = []
        else:
            current.append(ch)
    # Last segment
    segment = "".join(current).strip()
    if segment:
        entries.append(segment)

    # Normalize each entry
    result: list[dict[str, Any]] = []
    for entry in entries:
        norm = normalize_ingredient_name(entry)
        if norm:
            result.append({"raw": entry, "normalized": norm})

    return result


def resolve_ingredient(
    name_or_normalized: str,
    db: Session,
) -> dict[str, Any]:
    """Resolve an ingredient name to its database record.

    Behavior:
    - Match by normalized_name first
    - Fall back to alias_normalized in ingredient_aliases table
    - If no match and db is provided, create an "unreviewed" ingredient entry
    - If no db provided, return the best guess or None

    Returns dict with keys: {id, name, normalized_name, is_new}
    """
    from app.database.models import Ingredient, IngredientAlias

    normalized = normalize_ingredient_name(name_or_normalized)

    # Try matching by normalized_name
    ingredient = db.query(Ingredient).filter(
        Ingredient.normalized_name == normalized
    ).first()

    if ingredient:
        return {
            "id": ingredient.id,
            "name": ingredient.name,
            "normalized_name": ingredient.normalized_name,
            "is_new": False,
        }

    # Try matching by alias
    alias = (
        db.query(IngredientAlias)
        .filter(IngredientAlias.alias_normalized == normalized)
        .first()
    )

    if alias:
        # Return the linked ingredient
        ing = db.get(Ingredient, alias.ingredient_id)
        if ing:
            return {
                "id": ing.id,
                "name": ing.name,
                "normalized_name": ing.normalized_name,
                "is_new": False,
            }

    # No match: create an "unreviewed" ingredient
    new_ing = Ingredient(
        name=name_or_normalized,
        normalized_name=normalized,
        category_function="other",
    )
    db.add(new_ing)
    db.commit()
    db.refresh(new_ing)

    return {
        "id": new_ing.id,
        "name": new_ing.name,
        "normalized_name": new_ing.normalized_name,
        "is_new": True,
    }