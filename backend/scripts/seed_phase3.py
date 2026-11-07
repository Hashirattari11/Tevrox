"""Seed the development database with development-only catalogue data.

This script is intentionally explicit about being development data. It is safe
to run repeatedly: existing rows (matched by unique keys such as ``barcode``,
``normalized_name``, and ``alias_normalized``) are skipped rather than
duplicated.

It must not be used against production. When ENVIRONMENT=production this
script refuses to run unless ``--i-know-what-i-am-doing`` is passed.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.config import get_settings
from app.database.models import (
    Brand,
    Ingredient,
    IngredientAlias,
    Product,
    VerificationStatus,
)
from app.database.session import SessionLocal
from app.modules.ingredients.service import (
    link_product_ingredients,
    normalize_ingredient_name,
)
from app.modules.products.service import get_source

DEV_PREFIX = "[Development seed]"

# (name, function, description, aliases)
INGREDIENTS: list[tuple[str, str, str, list[str]]] = [
    ("Aqua", "solvent", "Water.", ["water", "eau", "aqua purificata"]),
    ("Glycerin", "humectant", "Humectant that attracts water to the skin.",
     ["glycerol", "gylcerin"]),
    ("Niacinamide", "active", "Vitamin B3. Supports barrier function and tone.",
     ["vitamin b3", "nicotinamide"]),
    ("Hyaluronic Acid", "humectant", "High molecular weight humectant.",
     ["hyaluronan"]),
    ("Sodium Hyaluronate", "humectant", "Sodium salt of hyaluronic acid.",
     ["hyaluronan sodium"]),
    ("Squalane", "emollient", "Skin-identical lipid emollient.", ["squalane"]),
    ("Ceramide NP", "emollient", "Barrier-supportive ceramide.",
     ["ceramide 3", "ceramide np"]),
    ("Panthenol", "humectant", "Provitamin B5.",
     ["provitamin b5", "dexpanthenol"]),
    ("Allantoin", "active", "Soothing skin-conditioning agent.", ["allantoin"]),
    ("Tocopherol", "antioxidant", "Vitamin E antioxidant.",
     ["vitamin e", "alpha tocopherol"]),
    ("Ascorbic Acid", "antioxidant", "Vitamin C.",
     ["vitamin c", "l-ascorbic acid"]),
    ("Retinol", "active", "Vitamin A derivative for texture and tone.",
     ["vitamin a", "retinoid"]),
    ("Salicylic Acid", "active", "Beta hydroxy acid for exfoliation.",
     ["bha", "2-hydroxybenzoic acid"]),
    ("Glycolic Acid", "active", "Alpha hydroxy acid for surface exfoliation.",
     ["aha", "hydroxyacetic acid"]),
    ("Lactic Acid", "active", "Alpha hydroxy acid and humectant.",
     ["2-hydroxypropanoic acid"]),
    ("Citric Acid", "buffer", "pH adjuster.",
     ["2-hydroxy-1,2,3-propanetricarboxylic acid"]),
    ("Sodium Hydroxide", "buffer", "pH adjuster.", ["caustic soda", "lye"]),
    ("Phenoxyethanol", "preservative", "Broad-spectrum preservative.",
     ["phenoxyethanol"]),
    ("Ethylhexylglycerin", "preservative", "Preservative booster.",
     ["octylglycerin"]),
    ("Caprylyl Glycol", "preservative",
     "Skin-conditioning preservative booster.", ["1,2-octanediol"]),
    ("Sodium Benzoate", "preservative", "Preservative.",
     ["benzoate of soda"]),
    ("Potassium Sorbate", "preservative", "Preservative.",
     ["sorbic acid potassium salt"]),
    ("Benzyl Alcohol", "preservative",
     "Preservative and fragrance; may sensitise.", ["phenylmethanol"]),
    ("Parfum", "fragrance", "Fragrance blend; common sensitiser.",
     ["fragrance", "aroma"]),
    ("Linalool", "fragrance", "Fragrance allergen.", ["linalool"]),
    ("Limonene", "fragrance", "Fragrance allergen.", ["d-limonene"]),
    ("Citral", "fragrance", "Fragrance allergen.", ["citral"]),
    ("Coumarin", "fragrance", "Fragrance allergen.", ["coumarin"]),
    ("Sodium Laureth Sulfate", "surfactant", "Anionic surfactant.",
     ["sles", "sodium laureth sulfate"]),
    ("Sodium Lauryl Sulfate", "surfactant", "Anionic surfactant.", ["sls"]),
    ("Cocamidopropyl Betaine", "surfactant",
     "Amphoteric surfactant.", ["capb"]),
    ("Decyl Glucoside", "surfactant",
     "Mild non-ionic surfactant.", ["decyl glucoside"]),
    ("Polysorbate 20", "surfactant",
     "Non-ionic emulsifier and solubilising agent.", ["tween 20"]),
    ("Cetearyl Alcohol", "emollient",
     "Fatty alcohol emollient and thickener.", ["cetostearyl alcohol"]),
    ("Glyceryl Stearate", "emollient",
     "Emulsifier and emollient.", ["glyceryl monostearate"]),
    ("Dimethicone", "emollient", "Silicone emollient.",
     ["polydimethylsiloxane"]),
    ("Isopropyl Myristate", "emollient", "Ester emollient.", ["ipm"]),
    ("Butyrospermum Parkii Butter", "emollient",
     "Shea butter.", ["shea butter", "shea"]),
    ("Tocopheryl Acetate", "antioxidant", "Vitamin E ester.",
     ["vitamin e acetate"]),
    ("Sodium Chloride", "other", "Viscosity modifier.", ["salt"]),
    ("Xanthan Gum", "other", "Rheology modifier.",
     ["xanthomonas campestris polysaccharide"]),
    ("Carbomer", "other", "Gelling agent.", ["carbopol"]),
    ("Disodium EDTA", "buffer", "Chelating agent.", ["edta"]),
    ("Titanium Dioxide", "uv_filter", "Mineral UV filter.",
     ["tio2", "titanium dioxide"]),
    ("Zinc Oxide", "uv_filter", "Mineral UV filter.",
     ["zno", "zinc oxide"]),
    ("Avobenzone", "uv_filter", "Organic UV filter.",
     ["butyl methoxydibenzoylmethane"]),
    ("Bis-Ethylhexyloxyphenol Methoxyphenyl Triazine", "uv_filter",
     "Broad-spectrum organic UV filter.", ["tinosorb s"]),
    ("Octocrylene", "uv_filter", "Organic UV filter.", ["octocrylene"]),
    ("Alcohol", "solvent", "Denatured alcohol.",
     ["ethanol", "ethyl alcohol", "sd alcohol"]),
    ("Butylene Glycol", "solvent", "Solvent and humectant.", ["1,3-butanediol"]),
    ("Propanediol", "solvent", "Solvent and humectant.", ["1,3-propanediol"]),
]

# (name, brand, category, barcode, ingredients_text)
PRODUCTS: list[tuple[str, str, str, str, str]] = [
    ("Gentle Foam Cleanser", "Tevrox Development", "cleanser", "4006381000001",
     "Aqua, Glycerin, Cocamidopropyl Betaine, Decyl Glucoside, Panthenol, "
     "Sodium Chloride, Phenoxyethanol, Ethylhexylglycerin"),
    ("Hydra Gel Moisturiser", "Tevrox Development", "moisturizer", "4006381000002",
     "Aqua, Glycerin, Sodium Hyaluronate, Panthenol, Niacinamide, Carbomer, "
     "Disodium EDTA, Phenoxyethanol"),
    ("Daily Renewal Serum", "Tevrox Development", "serum", "4006381000003",
     "Aqua, Glycerin, Niacinamide 10%, Panthenol, Tocopherol, "
     "Phenoxyethanol, Ethylhexylglycerin"),
    ("Mineral SPF 50", "Tevrox Development", "sunscreen", "4006381000004",
     "Aqua, Zinc Oxide, Titanium Dioxide, Glycerin, Caprylyl Glycol, "
     "Phenoxyethanol"),
    ("Overnight Retinol Cream", "Tevrox Development", "treatment", "4006381000005",
     "Aqua, Glycerin, Retinol, Ceramide NP, Squalane, "
     "Butyrospermum Parkii Butter, Phenoxyethanol"),
    ("Exfoliating AHA Toner", "Tevrox Development", "toner", "4006381000006",
     "Aqua, Glycolic Acid, Lactic Acid, Glycerin, Panthenol, Citric Acid, "
     "Sodium Hydroxide, Phenoxyethanol"),
    ("Brightening Vitamin C Serum", "Tevrox Development", "serum", "4006381000007",
     "Aqua, Ascorbic Acid, Glycerin, Tocopherol, Disodium EDTA, "
     "Phenoxyethanol"),
    ("Barrier Repair Cream", "Tevrox Development", "moisturizer", "4006381000008",
     "Aqua, Glycerin, Ceramide NP, Squalane, Glyceryl Stearate, "
     "Cetearyl Alcohol, Phenoxyethanol"),
    ("Clay Purifying Mask", "Tevrox Development", "mask", "4006381000009",
     "Aqua, Sodium Chloride, Glycerin, Allantoin, Phenoxyethanol, "
     "Caprylyl Glycol"),
    ("Niacinamide Balancing Toner", "Tevrox Development", "toner", "4006381000010",
     "Aqua, Niacinamide, Glycerin, Panthenol, Allantoin, Phenoxyethanol"),
]


def seed(session) -> dict[str, int]:
    summary = {
        "ingredients_created": 0,
        "ingredients_skipped": 0,
        "aliases_created": 0,
        "aliases_skipped": 0,
        "products_created": 0,
        "products_skipped": 0,
        "brands_created": 0,
    }

    source = get_source(session, "development_seed")

    for name, function, description, aliases in INGREDIENTS:
        normalized = normalize_ingredient_name(name)
        ingredient = session.scalar(
            select(Ingredient).where(Ingredient.normalized_name == normalized)
        )
        if ingredient is None:
            ingredient = Ingredient(
                name=name,
                normalized_name=normalized,
                category_function=function,
                description=f"{DEV_PREFIX} {description}",
                is_reviewed=True,
                is_active=True,
            )
            session.add(ingredient)
            session.flush()
            summary["ingredients_created"] += 1
        else:
            summary["ingredients_skipped"] += 1

        for alias in aliases:
            alias_normalized = normalize_ingredient_name(alias)
            existing_alias = session.scalar(
                select(IngredientAlias).where(
                    IngredientAlias.alias_normalized == alias_normalized
                )
            )
            if existing_alias is not None:
                summary["aliases_skipped"] += 1
                continue
            session.add(
                IngredientAlias(
                    ingredient_id=ingredient.id,
                    alias_normalized=alias_normalized,
                )
            )
            summary["aliases_created"] += 1

    for name, brand_name, category, barcode, ingredients_text in PRODUCTS:
        existing = session.scalar(
            select(Product).where(Product.barcode == barcode)
        )
        brand = session.scalar(
            select(Brand).where(Brand.name == brand_name)
        )
        if brand is None:
            brand = Brand(name=brand_name)
            session.add(brand)
            session.flush()
            summary["brands_created"] += 1

        if existing is not None:
            summary["products_skipped"] += 1
            continue

        product = Product(
            name=name,
            barcode=barcode,
            category=category,
            description=(
                f"{DEV_PREFIX} Sample product for local and test environments."
            ),
            verification_status=VerificationStatus.verified,
            verified_at=datetime.now(UTC),
            source_id=source.id,
            brand_id=brand.id,
            ingredients_raw_text=ingredients_text,
            is_active=True,
        )
        session.add(product)
        session.flush()
        link_product_ingredients(product, ingredients_text, session)
        summary["products_created"] += 1

    session.commit()
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--i-know-what-i-am-doing",
        action="store_true",
        help="Required when ENVIRONMENT=production",
    )
    args = parser.parse_args()

    settings = get_settings()
    print(f"Tevrox Phase 3 seed against: {settings.database_url}")
    print(f"Environment: {settings.environment}")
    if settings.environment == "production" and not args.i_know_what_i_am_doing:
        print(
            "Refusing to seed a production database. "
            "Pass --i-know-what-i-am-doing to override."
        )
        return 1

    with SessionLocal() as session:
        summary = seed(session)

    print("Seed complete.")
    for key, value in sorted(summary.items()):
        print(f"  {key}: {value}")
    print(f"Descriptions are prefixed with {DEV_PREFIX!r}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
