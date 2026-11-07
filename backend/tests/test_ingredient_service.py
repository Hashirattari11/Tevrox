"""Ingredient normalization, parsing, resolution, linking, and merge tests."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models import Brand, Ingredient, Product, ProductIngredient
from app.modules.ingredients.service import (
    link_product_ingredients,
    merge_ingredients,
    normalize_ingredient_name,
    parse_ingredient_list,
    resolve_ingredient,
)
from app.modules.products.service import get_source


def test_normalize_handles_common_label_noise() -> None:
    assert normalize_ingredient_name("  Niacinamide 10% ") == "niacinamide"
    assert normalize_ingredient_name("Retinol (Vitamin A)") == "retinol (vitamin a)"
    assert normalize_ingredient_name("Aqua / Water") == "aqua / water"
    assert normalize_ingredient_name("GLYCERIN.") == "glycerin"
    assert normalize_ingredient_name("Retinol (10%)") == "retinol"
    assert normalize_ingredient_name(None) == ""
    assert normalize_ingredient_name("   ") == ""


def test_normalize_applies_unicode_nfkc() -> None:
    # Full-width characters normalize to their ASCII equivalents.
    assert normalize_ingredient_name("Ｖｉｔａｍｉｎ Ｃ") == "vitamin c"


def test_parse_ingredient_list_handles_prefixes_and_nested_commas() -> None:
    raw = (
        "Ingredients: Aqua (Water), Glycerin, Niacinamide 10%, "
        "Phenoxyethanol (and) Ethylhexylglycerin, Parfum."
    )
    parsed = parse_ingredient_list(raw)

    assert [entry["normalized"] for entry in parsed] == [
        "aqua (water)",
        "glycerin",
        "niacinamide",
        "phenoxyethanol (and) ethylhexylglycerin",
        "parfum",
    ]
    assert parsed[0]["raw"] == "Aqua (Water)"


def test_parse_ingredient_list_splits_newlines_and_bullets() -> None:
    parsed = parse_ingredient_list(
        "INCI:\n• Squalane\n• Tocopherol\n- Panthenol"
    )
    assert [entry["normalized"] for entry in parsed] == [
        "squalane",
        "tocopherol",
        "panthenol",
    ]


def test_parse_ingredient_list_preserves_every_identifiable_entry() -> None:
    parsed = parse_ingredient_list("Aqua, , Glycerin, Aqua, Totally Unknown Extract")
    assert [entry["normalized"] for entry in parsed] == [
        "aqua",
        "glycerin",
        "aqua",
        "totally unknown extract",
    ]


def test_parse_ingredient_list_returns_empty_for_blank() -> None:
    assert parse_ingredient_list(None) == []
    assert parse_ingredient_list("") == []
    assert parse_ingredient_list("   ,  ;  ") == []


def test_resolve_ingredient_creates_unreviewed_rows(db_session: Session) -> None:
    resolved = resolve_ingredient("Niacinamide", db_session)

    assert resolved["is_new"] is True
    assert resolved["is_reviewed"] is False
    ingredient = db_session.get(Ingredient, resolved["id"])
    assert ingredient is not None
    assert ingredient.normalized_name == "niacinamide"
    assert ingredient.is_reviewed is False
    assert ingredient.is_active is True


def test_resolve_ingredient_matches_alias(db_session: Session) -> None:
    from app.database.models import IngredientAlias

    ingredient = Ingredient(name="Aqua", normalized_name="aqua", is_reviewed=True)
    db_session.add(ingredient)
    db_session.flush()
    db_session.add(IngredientAlias(ingredient_id=ingredient.id, alias_normalized="water"))
    db_session.commit()

    resolved = resolve_ingredient("Water", db_session)

    assert resolved["id"] == ingredient.id
    assert resolved["is_new"] is False


def test_link_product_ingredients_never_drops_unknowns(db_session: Session) -> None:
    source = get_source(db_session, "user_submitted")
    product = Product(
        name="Mystery Serum",
        category="serum",
        source_id=source.id,
        verification_status="unverified",
    )
    db_session.add(product)
    db_session.flush()

    linked = link_product_ingredients(
        product, "Aqua, Unobtainium Extract, Glycerin", db_session
    )
    db_session.commit()

    assert len(linked) == 3
    names = {entry["normalized_name"] for entry in linked}
    assert names == {"aqua", "unobtainium extract", "glycerin"}
    links = db_session.query(ProductIngredient).filter_by(product_id=product.id).all()
    assert len(links) == 3
    unreviewed = (
        db_session.query(Ingredient)
        .filter(Ingredient.normalized_name == "unobtainium extract")
        .one()
    )
    assert unreviewed.is_reviewed is False


def test_link_product_ingredients_deduplicates_join_rows(db_session: Session) -> None:
    source = get_source(db_session, "user_submitted")
    product = Product(
        name="Duplicate Label",
        category="serum",
        source_id=source.id,
        verification_status="unverified",
    )
    db_session.add(product)
    db_session.flush()

    linked = link_product_ingredients(product, "Aqua, Aqua, Glycerin", db_session)
    db_session.commit()

    assert len(linked) == 2
    assert product.ingredients_raw_text == "Aqua, Aqua, Glycerin"


def test_merge_ingredients_moves_links_and_aliases(db_session: Session) -> None:
    from app.database.models import IngredientAlias

    source_ing = Ingredient(name="Water", normalized_name="water", is_reviewed=False)
    target_ing = Ingredient(name="Aqua", normalized_name="aqua", is_reviewed=False)
    db_session.add_all([source_ing, target_ing])
    db_session.flush()

    source = get_source(db_session, "user_submitted")
    product = Product(
        name="Merged Product",
        category="other",
        source_id=source.id,
        verification_status="unverified",
    )
    db_session.add(product)
    db_session.flush()
    db_session.add(
        ProductIngredient(
            product_id=product.id, ingredient_id=source_ing.id, position=0
        )
    )
    db_session.add(
        IngredientAlias(ingredient_id=source_ing.id, alias_normalized="eau")
    )
    db_session.commit()

    result = merge_ingredients(source_ing.id, target_ing.id, db_session)
    db_session.commit()

    assert result["moved_product_ingredients"] == 1
    assert result["moved_aliases"] == 1
    link = (
        db_session.query(ProductIngredient).filter_by(product_id=product.id).one()
    )
    assert link.ingredient_id == target_ing.id
    db_session.refresh(source_ing)
    assert source_ing.is_active is False
    assert target_ing.is_reviewed is True


def test_merge_rejects_self_and_missing_ids(db_session: Session) -> None:
    ingredient = Ingredient(name="Aqua", normalized_name="aqua")
    db_session.add(ingredient)
    db_session.commit()

    try:
        merge_ingredients(ingredient.id, ingredient.id, db_session)
    except ValueError as exc:
        assert "itself" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("expected ValueError")

    import uuid

    try:
        merge_ingredients(ingredient.id, uuid.uuid4(), db_session)
    except LookupError:
        pass
    else:  # pragma: no cover - defensive
        raise AssertionError("expected LookupError")


def test_brand_model_is_available_for_ingredient_tests() -> None:
    # Guards against accidental model import regressions in this module.
    assert Brand.__tablename__ == "brands"
