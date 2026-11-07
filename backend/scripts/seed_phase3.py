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

# Each entry:
# (name, category_function, description, aliases, function_tags, safety_notes, irritation_potential)
# All descriptions/notes are plain educational wording, marked as development
# data and to be reviewed by a qualified person before launch.
INGREDIENTS: list[tuple] = [
    # name, function, description, aliases, function_tags, safety_notes, irritation_potential
    (
        "Aqua", "solvent", "Water, used as a base solvent in formulations.",
        ["water", "eau", "aqua purificata"],
        ["solvent", "water-base"],
        "Generally considered safe and non-irritating at typical use levels.",
        "low",
    ),
    (
        "Glycerin", "humectant", "Humectant that attracts water to the skin.",
        ["glycerol", "gylcerin"],
        ["humectant", "skin-conditioning"],
        "Well tolerated; high concentrations may feel sticky on skin.",
        "low",
    ),
    (
        "Niacinamide", "active", "Vitamin B3. Supports barrier function and tone.",
        ["vitamin b3", "nicotinamide"],
        ["active", "barrier-support", "brightening"],
        "Generally well tolerated; rare reports of mild flushing.",
        "low",
    ),
    (
        "Hyaluronic Acid", "humectant", "High molecular weight humectant.",
        ["hyaluronan"],
        ["humectant", "hydration"],
        "Generally considered safe and non-irritating.",
        "low",
    ),
    (
        "Sodium Hyaluronate", "humectant", "Sodium salt of hyaluronic acid.",
        ["hyaluronan sodium"],
        ["humectant", "hydration"],
        "Generally considered safe and non-irritating.",
        "low",
    ),
    (
        "Squalane", "emollient", "Skin-identical lipid emollient.",
        ["squalane"],
        ["emollient", "lipid"],
        "Generally well tolerated; low irritation potential.",
        "low",
    ),
    (
        "Ceramide NP", "emollient", "Barrier-supportive ceramide.",
        ["ceramide 3", "ceramide np"],
        ["emollient", "barrier-repair", "lipid"],
        "Generally considered safe; mimics skin's natural lipids.",
        "low",
    ),
    (
        "Panthenol", "humectant", "Provitamin B5.",
        ["provitamin b5", "dexpanthenol"],
        ["humectant", "skin-soothing"],
        "Generally well tolerated; rare sensitivity reports.",
        "low",
    ),
    (
        "Allantoin", "active", "Soothing skin-conditioning agent.",
        ["allantoin"],
        ["active", "skin-soothing", "keratolytic"],
        "Generally considered safe and non-irritating.",
        "low",
    ),
    (
        "Tocopherol", "antioxidant", "Vitamin E antioxidant.",
        ["vitamin e", "alpha tocopherol"],
        ["antioxidant", "skin-conditioning"],
        "Generally safe; rare contact sensitivity reported.",
        "low",
    ),
    (
        "Ascorbic Acid", "antioxidant", "Vitamin C.",
        ["vitamin c", "l-ascorbic acid"],
        ["antioxidant", "brightening", "active"],
        "Can cause tingling or irritation at high concentrations, especially on sensitive skin.",
        "moderate",
    ),
    (
        "Retinol", "active", "Vitamin A derivative for texture and tone.",
        ["vitamin a", "retinoid"],
        ["active", "anti-aging", "exfoliant"],
        "Can cause dryness, redness, peeling; introduce gradually. Avoid in "
        "pregnancy without medical advice.",
        "moderate",
    ),
    (
        "Salicylic Acid", "active", "Beta hydroxy acid for exfoliation.",
        ["bha", "2-hydroxybenzoic acid"],
        ["active", "exfoliant", "acne"],
        "Can cause dryness and irritation; avoid overuse on sensitive skin.",
        "moderate",
    ),
    (
        "Glycolic Acid", "active", "Alpha hydroxy acid for surface exfoliation.",
        ["aha", "hydroxyacetic acid"],
        ["active", "exfoliant", "brightening"],
        "Can cause stinging, redness, and sun sensitivity; use sunscreen.",
        "moderate",
    ),
    (
        "Lactic Acid", "active", "Alpha hydroxy acid and humectant.",
        ["2-hydroxypropanoic acid"],
        ["active", "exfoliant", "humectant"],
        "Milder AHA; can still cause irritation on sensitive skin.",
        "moderate",
    ),
    (
        "Citric Acid", "buffer", "pH adjuster.",
        ["2-hydroxy-1,2,3-propanetricarboxylic acid"],
        ["buffer", "chelating-agent"],
        "Generally safe at low concentrations; may irritate at higher levels.",
        "low",
    ),
    (
        "Sodium Hydroxide", "buffer", "pH adjuster.",
        ["caustic soda", "lye"],
        ["buffer"],
        "Used in small amounts to balance pH; not a leave-on active ingredient.",
        "low",
    ),
    (
        "Phenoxyethanol", "preservative", "Broad-spectrum preservative.",
        ["phenoxyethanol"],
        ["preservative"],
        "Generally considered safe; rare sensitivity reports at higher concentrations.",
        "low",
    ),
    (
        "Ethylhexylglycerin", "preservative", "Preservative booster.",
        ["octylglycerin"],
        ["preservative", "skin-conditioning"],
        "Generally well tolerated; low irritation potential.",
        "low",
    ),
    (
        "Caprylyl Glycol", "preservative", "Skin-conditioning preservative booster.",
        ["1,2-octanediol"],
        ["preservative", "skin-conditioning"],
        "Generally considered safe and non-irritating.",
        "low",
    ),
    (
        "Sodium Benzoate", "preservative", "Preservative.",
        ["benzoate of soda"],
        ["preservative"],
        "Generally safe; can form benzene with ascorbic acid under certain "
        "conditions (rare in cosmetics).",
        "low",
    ),
    (
        "Potassium Sorbate", "preservative", "Preservative.",
        ["sorbic acid potassium salt"],
        ["preservative"],
        "Generally considered safe; low irritation potential.",
        "low",
    ),
    (
        "Benzyl Alcohol", "preservative", "Preservative and fragrance; may sensitise.",
        ["phenylmethanol"],
        ["preservative", "fragrance"],
        "Can cause irritation or allergic contact dermatitis in sensitive individuals.",
        "moderate",
    ),
    (
        "Parfum", "fragrance", "Fragrance blend; common sensitiser.",
        ["fragrance", "aroma"],
        ["fragrance"],
        "Common allergen; may cause irritation or contact dermatitis in sensitive skin.",
        "moderate",
    ),
    (
        "Linalool", "fragrance", "Fragrance allergen.",
        ["linalool"],
        ["fragrance", "allergen"],
        "EU-declared allergen; may cause sensitization.",
        "moderate",
    ),
    (
        "Limonene", "fragrance", "Fragrance allergen.",
        ["d-limonene"],
        ["fragrance", "allergen"],
        "EU-declared allergen; can oxidize and become more sensitizing.",
        "moderate",
    ),
    (
        "Citral", "fragrance", "Fragrance allergen.",
        ["citral"],
        ["fragrance", "allergen"],
        "EU-declared allergen; may cause irritation.",
        "moderate",
    ),
    (
        "Coumarin", "fragrance", "Fragrance allergen.",
        ["coumarin"],
        ["fragrance", "allergen"],
        "EU-declared allergen; potential sensitizer.",
        "moderate",
    ),
    (
        "Sodium Laureth Sulfate", "surfactant", "Anionic surfactant.",
        ["sles", "sodium laureth sulfate"],
        ["surfactant", "foaming-agent"],
        "Can be drying or irritating, especially on sensitive or dry skin.",
        "moderate",
    ),
    (
        "Sodium Lauryl Sulfate", "surfactant", "Anionic surfactant.",
        ["sls"],
        ["surfactant", "foaming-agent"],
        "Can be drying and irritating; higher irritation potential than SLES.",
        "moderate",
    ),
    (
        "Cocamidopropyl Betaine", "surfactant", "Amphoteric surfactant.",
        ["capb"],
        ["surfactant", "foaming-agent"],
        "Generally mild; rare reports of sensitization.",
        "low",
    ),
    (
        "Decyl Glucoside", "surfactant", "Mild non-ionic surfactant.",
        ["decyl glucoside"],
        ["surfactant", "mild-cleanser"],
        "Generally considered gentle and non-irritating.",
        "low",
    ),
    (
        "Polysorbate 20", "surfactant", "Non-ionic emulsifier and solubilising agent.",
        ["tween 20"],
        ["surfactant", "emulsifier"],
        "Generally considered safe and non-irritating.",
        "low",
    ),
    (
        "Cetearyl Alcohol", "emollient", "Fatty alcohol emollient and thickener.",
        ["cetostearyl alcohol"],
        ["emollient", "thickener", "fatty-alcohol"],
        "Not a drying alcohol; generally well tolerated.",
        "low",
    ),
    (
        "Glyceryl Stearate", "emollient", "Emulsifier and emollient.",
        ["glyceryl monostearate"],
        ["emollient", "emulsifier"],
        "Generally considered safe and non-irritating.",
        "low",
    ),
    (
        "Dimethicone", "emollient", "Silicone emollient.",
        ["polydimethylsiloxane"],
        ["emollient", "occlusive", "silicone"],
        "Generally considered safe; low skin penetration.",
        "low",
    ),
    (
        "Isopropyl Myristate", "emollient", "Ester emollient.",
        ["ipm"],
        ["emollient", "occlusive"],
        "Can be comedogenic for some acne-prone skin types.",
        "low",
    ),
    (
        "Butyrospermum Parkii Butter", "emollient", "Shea butter.",
        ["shea butter", "shea"],
        ["emollient", "lipid", "natural"],
        "Generally considered safe; rare allergy reports.",
        "low",
    ),
    (
        "Tocopheryl Acetate", "antioxidant", "Vitamin E ester.",
        ["vitamin e acetate"],
        ["antioxidant", "skin-conditioning"],
        "Generally safe; stable form of vitamin E.",
        "low",
    ),
    (
        "Sodium Chloride", "other", "Viscosity modifier.",
        ["salt"],
        ["thickener", "mineral"],
        "Generally safe at cosmetic concentrations.",
        "low",
    ),
    (
        "Xanthan Gum", "other", "Rheology modifier.",
        ["xanthomonas campestris polysaccharide"],
        ["thickener", "stabilizer"],
        "Generally considered safe and non-irritating.",
        "low",
    ),
    (
        "Carbomer", "other", "Gelling agent.",
        ["carbopol"],
        ["thickener", "gelling-agent"],
        "Generally considered safe; neutralized forms are non-irritating.",
        "low",
    ),
    (
        "Disodium EDTA", "buffer", "Chelating agent.",
        ["edta"],
        ["chelating-agent", "buffer"],
        "Generally considered safe at cosmetic concentrations.",
        "low",
    ),
    (
        "Titanium Dioxide", "uv_filter", "Mineral UV filter.",
        ["tio2", "titanium dioxide"],
        ["uv-filter", "mineral-sunscreen"],
        "Generally considered safe in non-nano form for topical use.",
        "low",
    ),
    (
        "Zinc Oxide", "uv_filter", "Mineral UV filter.",
        ["zno", "zinc oxide"],
        ["uv-filter", "mineral-sunscreen"],
        "Generally considered safe; broad-spectrum UV protection.",
        "low",
    ),
    (
        "Avobenzone", "uv_filter", "Organic UV filter.",
        ["butyl methoxydibenzoylmethane"],
        ["uv-filter", "organic-sunscreen"],
        "Can be photounstable; often paired with stabilizers.",
        "low",
    ),
    (
        "Bis-Ethylhexyloxyphenol Methoxyphenyl Triazine", "uv_filter",
        "Broad-spectrum organic UV filter.",
        ["tinosorb s"],
        ["uv-filter", "broad-spectrum"],
        "Generally considered safe and photostable.",
        "low",
    ),
    (
        "Octocrylene", "uv_filter", "Organic UV filter.",
        ["octocrylene"],
        ["uv-filter", "organic-sunscreen"],
        "Generally considered safe; rare sensitivity reports.",
        "low",
    ),
    (
        "Alcohol", "solvent", "Denatured alcohol.",
        ["ethanol", "ethyl alcohol", "sd alcohol"],
        ["solvent", "drying-alcohol"],
        "Can be drying and irritating, especially on dry or sensitive skin.",
        "moderate",
    ),
    (
        "Butylene Glycol", "solvent", "Solvent and humectant.",
        ["1,3-butanediol"],
        ["solvent", "humectant"],
        "Generally considered safe; low irritation potential.",
        "low",
    ),
    (
        "Propanediol", "solvent", "Solvent and humectant.",
        ["1,3-propanediol"],
        ["solvent", "humectant"],
        "Generally considered safe and gentle.",
        "low",
    ),
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

    for entry in INGREDIENTS:
        (
            name, function, description, aliases, function_tags,
            safety_notes, irritation_potential,
        ) = entry
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
                function_tags=function_tags,
                safety_notes=f"{DEV_PREFIX} {safety_notes}",
                irritation_potential=irritation_potential,
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
    print(f"Tevrox Phase 4 seed against: {settings.database_url}")
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
    import sys as _sys
    _sys.exit(main())
