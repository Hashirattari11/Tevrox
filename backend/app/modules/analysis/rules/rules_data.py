"""Versioned, data-driven rules engine for ingredient analysis.

Rules are pure Python functions operating on ingredient data plus user
profile context. Each rule has an id, description, severity, and a source
note so a non-developer can review them.

All rules are flagged "needs expert review" until a qualified person signs off.
"""

from __future__ import annotations

RULES_VERSION = "v1"

# Each rule: id, description, severity, source_note, needs_expert_review
# severity: info | note | caution
RULES: list[dict[str, object]] = [
    {
        "id": "fragrance_present",
        "description": (
            "Fragrance or parfum is present in the ingredient list."
        ),
        "severity": "note",
        "source_note": (
            "Common allergen; EU requires declaration of 26 fragrance allergens."
        ),
        "needs_expert_review": True,
    },
    {
        "id": "drying_alcohol_present",
        "description": (
            "Drying alcohol (e.g. alcohol denat., SD alcohol, ethanol) is present."
        ),
        "severity": "note",
        "source_note": (
            "Can be drying, especially for dry or sensitive skin types."
        ),
        "needs_expert_review": True,
    },
    {
        "id": "active_ingredients_present",
        "description": (
            "Active ingredients present (retinoids, AHAs, BHAs, vitamin C)."
        ),
        "severity": "info",
        "source_note": (
            "General guidance: introduce actives gradually to allow skin to adapt."
        ),
        "needs_expert_review": True,
    },
    {
        "id": "comedogenic_tagged",
        "description": (
            "Comedogenic-tagged ingredients present (only if tagged in reference data)."
        ),
        "severity": "note",
        "source_note": (
            "May be relevant for oily skin or acne-prone users."
        ),
        "needs_expert_review": True,
    },
    {
        "id": "ingredient_order",
        "description": (
            "First 5 ingredients typically make up the bulk of the formula."
        ),
        "severity": "info",
        "source_note": (
            "Ingredients are listed in descending order of concentration in most regions."
        ),
        "needs_expert_review": True,
    },
    {
        "id": "unreviewed_ingredients",
        "description": (
            "More than 20% of ingredients are unreviewed or have limited information."
        ),
        "severity": "caution",
        "source_note": (
            "Unknown or unreviewed ingredients cannot be fully assessed."
        ),
        "needs_expert_review": True,
    },
]


def get_rules() -> list[dict[str, object]]:
    """Return the list of versioned rules."""
    return list(RULES)


def run_rules(
    *,
    ingredients: list[dict[str, object]],
    skin_type: str | None = None,
    skin_concerns: list[str] | None = None,
) -> list[dict[str, object]]:
    """Run all rules against ingredient data and user context.

    Args:
        ingredients: List of {id, name, normalized_name, function, is_reviewed, ...}
        skin_type: User's skin type from profile.
        skin_concerns: User's skin concerns from profile.

    Returns:
        List of findings: {rule_id, severity, ingredient_ids, message, relevant_to_user}
    """
    skin_concerns = skin_concerns or []
    concerns_lower = [c.lower() for c in skin_concerns]
    skin_type_lower = (skin_type or "").lower()

    findings: list[dict[str, object]] = []
    total = len(ingredients)
    unreviewed_count = 0

    for rule in RULES:
        rule_id = str(rule["id"])

        if rule_id == "fragrance_present":
            matched: list[str] = []
            for ing in ingredients:
                name = str(ing.get("name", "")).lower()
                if "fragrance" in name or "parfum" in name:
                    matched.append(str(ing.get("id", "")))
            if matched:
                relevant = "sensitive" in skin_type_lower or any(
                    c in concerns_lower for c in ("sensitivity", "redness")
                )
                findings.append({
                    "rule_id": rule_id,
                    "severity": "note",
                    "ingredient_ids": matched,
                    "message": (
                        "Fragrance is present in the product; people with "
                        "sensitive skin may want to patch test first."
                    ),
                    "relevant_to_user": relevant,
                })

        elif rule_id == "drying_alcohol_present":
            matched = []
            for ing in ingredients:
                name = str(ing.get("name", "")).lower()
                if (
                    "alcohol" in name
                    and "cetearyl" not in name
                    and "cetyl" not in name
                    and "stearyl" not in name
                    and "behenyl" not in name
                    and "isopropyl" not in name
                ):
                    matched.append(str(ing.get("id", "")))
            if matched:
                relevant = (
                    "dry" in skin_type_lower
                    or "sensitive" in skin_type_lower
                    or any(c in concerns_lower for c in ("dryness", "sensitivity"))
                )
                findings.append({
                    "rule_id": rule_id,
                    "severity": "note",
                    "ingredient_ids": matched,
                    "message": (
                        "Drying alcohol is present; it can be drying for some "
                        "skin types, especially dry or sensitive skin."
                    ),
                    "relevant_to_user": relevant,
                })

        elif rule_id == "active_ingredients_present":
            matched = []
            for ing in ingredients:
                name = str(ing.get("name", "")).lower()
                func = str(ing.get("function", "")).lower()
                if (
                    "retinol" in name
                    or "glycolic" in name
                    or "lactic" in name
                    or "salicylic" in name
                    or "ascorbic" in name
                    or "vitamin c" in name
                    or func == "active"
                ):
                    matched.append(str(ing.get("id", "")))
            if matched:
                findings.append({
                    "rule_id": rule_id,
                    "severity": "info",
                    "ingredient_ids": matched,
                    "message": (
                        "Active ingredients (e.g. retinoids, AHAs, BHAs, "
                        "vitamin C) are present. Introduce them gradually to "
                        "allow your skin to adapt."
                    ),
                    "relevant_to_user": True,
                })

        elif rule_id == "comedogenic_tagged":
            matched = []
            for ing in ingredients:
                tags = ing.get("function_tags") or []
                if any("comedogenic" in str(t).lower() for t in tags):
                    matched.append(str(ing.get("id", "")))
            if matched:
                relevant = (
                    "oily" in skin_type_lower
                    or any(c in concerns_lower for c in ("acne", "oiliness"))
                )
                findings.append({
                    "rule_id": rule_id,
                    "severity": "note",
                    "ingredient_ids": matched,
                    "message": (
                        "Comedogenic-tagged ingredients are present; may be "
                        "relevant for oily or acne-prone skin."
                    ),
                    "relevant_to_user": relevant,
                })

        elif rule_id == "ingredient_order":
            if total >= 5:
                first_five = [str(ing.get("id", "")) for ing in ingredients[:5]]
                findings.append({
                    "rule_id": rule_id,
                    "severity": "info",
                    "ingredient_ids": first_five,
                    "message": (
                        "The first 5 ingredients typically make up the bulk of "
                        "the formula (ingredients are listed in descending "
                        "order of concentration)."
                    ),
                    "relevant_to_user": True,
                })

        elif rule_id == "unreviewed_ingredients":
            for ing in ingredients:
                if not ing.get("is_reviewed", False):
                    unreviewed_count += 1
            if total > 0 and (unreviewed_count / total) > 0.2:
                unreviewed_ids = [
                    str(ing.get("id", ""))
                    for ing in ingredients
                    if not ing.get("is_reviewed", False)
                ]
                findings.append({
                    "rule_id": rule_id,
                    "severity": "caution",
                    "ingredient_ids": unreviewed_ids,
                    "message": (
                        "More than 20% of ingredients are unreviewed or have "
                        "limited information; treat the assessment as provisional."
                    ),
                    "relevant_to_user": True,
                })

    return findings
