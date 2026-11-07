"""Ingredient analysis service (Phase 4).

Implements the 7-step pipeline:
1. Retrieve product + ordered ingredients.
2. Normalize (use existing normalized records).
3. Reference (attach reference data per ingredient).
4. Rules (deterministic rules engine).
5. LLM (structured, minimal payload).
6. Validate (Pydantic + post-validation, retry once, fallback).
7. Display (store and return).
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.database.models import Analysis, Product, ProductIngredient, User
from app.integrations.ai_provider import (
    ProviderInvalidResponseError,
    ProviderRateLimitedError,
    ProviderUnavailableError,
    get_ai_provider,
)
from app.modules.analysis.prompts.system_prompt_v1 import (
    PROMPT_VERSION,
    get_system_prompt,
)
from app.modules.analysis.rules.engine import RULES_VERSION, run_rules
from app.modules.analysis.schemas import (
    BANNED_PHRASES,
    STANDARD_LIMITATIONS,
    AnalysisResult,
    KeyIngredient,
)

settings = get_settings()

# Per-user per-minute submission attempts (in-memory, per-process).
_submission_lock = threading.Lock()
_submission_attempts: dict[str, deque[float]] = defaultdict(deque)

# Daily limit key: user_id -> date -> count
_daily_lock = threading.Lock()
_daily_counts: dict[str, dict[str, int]] = defaultdict(dict)


def clear_rate_limits() -> None:
    """Test helper: reset in-memory rate limiters."""
    with _submission_lock:
        _submission_attempts.clear()
    with _daily_lock:
        _daily_counts.clear()


def _compute_input_hash(
    *,
    product_id: UUID,
    ingredient_ids: list[UUID],
    skin_type: str | None,
    skin_concerns: list[str],
) -> str:
    """Stable hash of the analysis input for cache lookups."""
    payload = {
        "product_id": str(product_id),
        "ingredient_ids": [str(i) for i in sorted(ingredient_ids)],
        "skin_type": skin_type or "",
        "skin_concerns": sorted(skin_concerns),
        "prompt_version": PROMPT_VERSION,
        "rules_version": RULES_VERSION,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def _enforce_rate_limits(user_id: UUID) -> None:
    """Enforce per-minute and daily limits. Raises HTTPException on breach."""
    now = time.monotonic()
    user_key = str(user_id)
    today = datetime.now(UTC).date().isoformat()

    # Per-minute limit (10 per minute)
    with _submission_lock:
        attempts = _submission_attempts[user_key]
        while attempts and attempts[0] <= now - 60:
            attempts.popleft()
        if len(attempts) >= 10:
            raise HTTPException(
                429,
                {
                    "code": "ANALYSIS_LIMIT_REACHED",
                    "message": "Too many analyses per minute. Please slow down.",
                },
            )
        attempts.append(now)

    # Daily limit
    with _daily_lock:
        day_counts = _daily_counts[user_key]
        used = day_counts.get(today, 0)
        if used >= settings.analysis_daily_limit:
            raise HTTPException(
                429,
                {
                    "code": "ANALYSIS_LIMIT_REACHED",
                    "message": "Daily analysis limit reached. Try again tomorrow.",
                },
            )
        day_counts[today] = used + 1


def _get_product_and_ingredients(
    db: Session, *, product_id: UUID
) -> tuple[Product, list[dict[str, Any]]]:
    """Step 1 & 2: Retrieve product and ordered ingredients."""
    product = db.scalar(
        select(Product)
        .options(
            selectinload(Product.product_ingredients).selectinload(
                ProductIngredient.ingredient
            )
        )
        .where(Product.id == product_id, Product.is_active.is_(True))
    )
    if product is None:
        raise HTTPException(
            404,
            {"code": "PRODUCT_NOT_FOUND", "message": "Product not found"},
        )

    links = sorted(
        product.product_ingredients or [],
        key=lambda link: (link.position is None, link.position or 0),
    )
    if not links:
        raise HTTPException(
            400,
            {
                "code": "ANALYSIS_NO_INGREDIENTS",
                "message": (
                    "This product has no parsed ingredients. Submit the product label first."
                ),
            },
        )

    ingredient_list: list[dict[str, Any]] = []
    for link in links:
        ing = link.ingredient
        if ing is None:
            continue
        ingredient_list.append({
            "id": str(ing.id),
            "name": ing.name,
            "normalized_name": ing.normalized_name,
            "function": ing.category_function or "other",
            "function_tags": ing.function_tags or [],
            "description": ing.description,
            "safety_notes": ing.safety_notes,
            "irritation_potential": ing.irritation_potential,
            "is_reviewed": ing.is_reviewed,
            "position": link.position,
            "original_text": link.original_text,
        })

    return product, ingredient_list


def _attach_reference_data(
    ingredients: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Step 3: Attach reference data (already on ingredient rows from DB)."""
    for ing in ingredients:
        if not ing.get("description") and not ing.get("safety_notes"):
            ing["_limited_information"] = True
    return ingredients


def _run_rules_engine(
    *,
    ingredients: list[dict[str, Any]],
    skin_type: str | None,
    skin_concerns: list[str],
) -> list[dict[str, Any]]:
    """Step 4: Run deterministic rules engine."""
    return run_rules(
        ingredients=ingredients,
        skin_type=skin_type,
        skin_concerns=skin_concerns,
    )


def _build_llm_payload(
    *,
    product_name: str,
    ingredients: list[dict[str, Any]],
    rule_findings: list[dict[str, Any]],
    skin_type: str | None,
    skin_concerns: list[str],
) -> dict[str, Any]:
    """Step 5: Build minimal, safe payload for the LLM (no personal data)."""
    return {
        "product_name": product_name,
        "ingredients": [
            {
                "id": ing["id"],
                "name": ing["name"],
                "function": ing.get("function", "other"),
                "function_tags": ing.get("function_tags", []),
                "description": ing.get("description"),
                "safety_notes": ing.get("safety_notes"),
                "irritation_potential": ing.get("irritation_potential"),
                "is_reviewed": ing.get("is_reviewed", False),
            }
            for ing in ingredients
        ],
        "rule_findings": rule_findings,
        "skin_type": skin_type,
        "skin_concerns": skin_concerns,
    }


def _has_banned_phrases(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in BANNED_PHRASES)


def _validate_and_merge(
    *,
    raw_data: dict[str, Any],
    rule_findings: list[dict[str, Any]],
    ingredients: list[dict[str, Any]],
) -> AnalysisResult:
    """Step 6: Validate AI output against Pydantic schema + post-validation."""
    input_ids = {ing["id"] for ing in ingredients}

    # Check for invented ingredient_ids.
    for ki in raw_data.get("key_ingredients", []):
        if str(ki.get("ingredient_id", "")) not in input_ids:
            raise ProviderInvalidResponseError(
                "AI_INVALID_RESPONSE",
                "AI referenced an ingredient not in the product.",
            )

    # Check banned phrases in all text fields.
    all_text = " ".join(
        [
            raw_data.get("summary", ""),
            raw_data.get("suitability_overview", ""),
            raw_data.get("confidence_reason", ""),
            *raw_data.get("cautions", []),
            *(
                ki.get("explanation", "")
                for ki in raw_data.get("key_ingredients", [])
            ),
        ]
    )
    if _has_banned_phrases(all_text):
        raise ProviderInvalidResponseError(
            "AI_INVALID_RESPONSE",
            "AI output contains banned medical-claim phrases.",
        )

    # Ensure caution-level rule findings are reflected in cautions.
    caution_findings = [f for f in rule_findings if f.get("severity") == "caution"]
    existing_cautions = set(raw_data.get("cautions", []))
    for finding in caution_findings:
        msg = str(finding.get("message", ""))
        if msg not in existing_cautions:
            existing_cautions.add(msg)

    # Merge standard limitations (backend-owned, always present).
    limitations = list(raw_data.get("limitations", []))
    for std in STANDARD_LIMITATIONS:
        if std not in limitations:
            limitations.append(std)

    return AnalysisResult(
        summary=raw_data.get("summary", "")[:600],
        suitability_overview=raw_data.get("suitability_overview", ""),
        key_ingredients=[
            KeyIngredient(
                ingredient_id=UUID(ki["ingredient_id"]),
                name=ki.get("name", "Unknown"),
                role=ki.get("role", "other"),
                explanation=ki.get("explanation", ""),
                caution_level=ki.get("caution_level", "info"),
            )
            for ki in raw_data.get("key_ingredients", [])
        ],
        cautions=list(existing_cautions),
        limitations=limitations,
        confidence=raw_data.get("confidence", "medium"),
        confidence_reason=raw_data.get("confidence_reason", ""),
    )


def _build_fallback_report(
    *,
    product_name: str,
    ingredients: list[dict[str, Any]],
    rule_findings: list[dict[str, Any]],
    skin_type: str | None,
    skin_concerns: list[str],
) -> AnalysisResult:
    """Build a safe rules-only fallback report (no LLM text)."""
    cautions: list[str] = []
    for f in rule_findings:
        if f.get("severity") == "caution":
            cautions.append(str(f.get("message", "")))

    key_ingredients = []
    for ing in ingredients[:6]:
        key_ingredients.append(KeyIngredient(
            ingredient_id=UUID(ing["id"]),
            name=ing.get("name", "Unknown ingredient"),
            role=ing.get("function", "other"),
            explanation=(
                f"{ing.get('name', 'This ingredient')} is in the product formula. "
                "Reference data is limited."
            ),
            caution_level="info",
        ))

    limitations = list(STANDARD_LIMITATIONS)
    limitations.append(
        "AI analysis was unavailable; this report is based on rules and reference data only."
    )

    return AnalysisResult(
        summary=(
            f"{product_name} contains {len(ingredients)} listed ingredient(s). "
            "AI analysis is currently unavailable; see cautions and limitations."
        ),
        suitability_overview=(
            f"Skin type: {skin_type or 'not specified'}. "
            f"Concerns: {', '.join(skin_concerns) if skin_concerns else 'none specified'}."
        ),
        key_ingredients=key_ingredients,
        cautions=cautions,
        limitations=limitations,
        confidence="low",
        confidence_reason=(
            "Fallback report; AI provider unavailable or output failed validation."
        ),
    )


def run_analysis(
    db: Session,
    *,
    user: User,
    product_id: UUID,
    force_refresh: bool = False,
) -> dict[str, Any]:
    """Run the full 7-step analysis pipeline and return the stored report."""
    # Get user profile for skin type/concerns.
    profile = user.user_profile if hasattr(user, "user_profile") else None
    skin_type = profile.skin_type if profile else None
    skin_concerns = profile.skin_concerns if profile else []

    # Step 1 & 2: Retrieve product + ingredients.
    product, ingredients = _get_product_and_ingredients(db, product_id=product_id)

    # Unverified product flag.
    product_unverified = str(product.verification_status) != "verified"

    # Input hash for caching.
    input_hash = _compute_input_hash(
        product_id=product_id,
        ingredient_ids=[ing["id"] for ing in ingredients],
        skin_type=skin_type,
        skin_concerns=skin_concerns,
    )

    # Cache hit: return existing completed analysis (not rate-limited).
    if not force_refresh:
        cached = db.scalar(
            select(Analysis).where(
                Analysis.user_id == user.id,
                Analysis.input_hash == input_hash,
                Analysis.status == "completed",
            )
        )
        if cached is not None:
            return {
                **_serialize_analysis(cached),
                "product_unverified": product_unverified,
            }

    # Rate limits (only for fresh analyses).
    _enforce_rate_limits(user.id)

    # Step 3: Attach reference data.
    ingredients = _attach_reference_data(ingredients)

    # Step 4: Rules engine.
    rule_findings = _run_rules_engine(
        ingredients=ingredients,
        skin_type=skin_type,
        skin_concerns=skin_concerns,
    )

    # Step 5 & 6: LLM + validate, with one retry, then fallback.
    system_prompt, _ = get_system_prompt()
    provider = get_ai_provider()

    llm_payload = _build_llm_payload(
        product_name=product.name,
        ingredients=ingredients,
        rule_findings=rule_findings,
        skin_type=skin_type,
        skin_concerns=skin_concerns,
    )

    result: AnalysisResult | None = None
    model_used = "fallback"
    input_tokens = None
    output_tokens = None
    latency_ms = None
    error_code: str | None = None
    status = "completed"

    try:
        provider_result = provider.generate_structured(
            system_prompt=system_prompt,
            user_payload=llm_payload,
            response_schema=AnalysisResult,
        )
        model_used = provider_result.model
        input_tokens = provider_result.input_tokens
        output_tokens = provider_result.output_tokens
        latency_ms = provider_result.latency_ms

        try:
            result = _validate_and_merge(
                raw_data=provider_result.data,
                rule_findings=rule_findings,
                ingredients=ingredients,
            )
        except ProviderInvalidResponseError:
            # Retry once with a corrective instruction.
            corrective_payload = dict(llm_payload)
            corrective_payload["_retry_instruction"] = (
                "Your previous response failed validation. "
                "Return ONLY valid JSON matching the schema. "
                "Do not invent ingredient IDs. Do not use medical claims."
            )
            provider_result2 = provider.generate_structured(
                system_prompt=system_prompt,
                user_payload=corrective_payload,
                response_schema=AnalysisResult,
            )
            model_used = provider_result2.model
            input_tokens = provider_result2.input_tokens
            output_tokens = provider_result2.output_tokens
            latency_ms = provider_result2.latency_ms
            result = _validate_and_merge(
                raw_data=provider_result2.data,
                rule_findings=rule_findings,
                ingredients=ingredients,
            )
    except (ProviderUnavailableError, ProviderRateLimitedError) as exc:
        error_code = exc.code
        status = "fallback"
        result = _build_fallback_report(
            product_name=product.name,
            ingredients=ingredients,
            rule_findings=rule_findings,
            skin_type=skin_type,
            skin_concerns=skin_concerns,
        )
    except ProviderInvalidResponseError:
        error_code = "AI_INVALID_RESPONSE"
        status = "fallback"
        result = _build_fallback_report(
            product_name=product.name,
            ingredients=ingredients,
            rule_findings=rule_findings,
            skin_type=skin_type,
            skin_concerns=skin_concerns,
        )

    # Step 7: Store and return.
    analysis = Analysis(
        user_id=user.id,
        product_id=product_id,
        structured_result=result.model_dump(),
        model_used=model_used,
        prompt_version=PROMPT_VERSION,
        rules_version=RULES_VERSION,
        input_hash=input_hash,
        status=status,
        latency_ms=latency_ms,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        error_code=error_code,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {
        **_serialize_analysis(analysis),
        "product_unverified": product_unverified,
    }


def _serialize_analysis(analysis: Analysis) -> dict[str, Any]:
    return {
        "id": str(analysis.id),
        "product_id": str(analysis.product_id) if analysis.product_id else None,
        "status": analysis.status,
        "model_used": analysis.model_used,
        "prompt_version": analysis.prompt_version,
        "rules_version": analysis.rules_version,
        "latency_ms": analysis.latency_ms,
        "input_tokens": analysis.input_tokens,
        "output_tokens": analysis.output_tokens,
        "error_code": analysis.error_code,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
        "result": analysis.structured_result,
    }


def get_analysis_history(
    db: Session, *, user: User, limit: int = 20, offset: int = 0
) -> tuple[list[dict[str, Any]], int]:
    """Get current user's analysis history, newest first."""
    stmt = (
        select(Analysis)
        .where(Analysis.user_id == user.id)
        .order_by(Analysis.created_at.desc())
    )
    count_stmt = select(func.count(Analysis.id)).where(Analysis.user_id == user.id)
    total = db.scalar(count_stmt) or 0
    rows = db.scalars(stmt.offset(offset).limit(limit)).all()
    return [_serialize_analysis(r) for r in rows], total


def get_analysis_by_id(
    db: Session, *, analysis_id: UUID, user: User
) -> dict[str, Any]:
    """Get a single analysis; only the owner may read it."""
    analysis = db.scalar(
        select(Analysis).where(
            Analysis.id == analysis_id, Analysis.user_id == user.id
        )
    )
    if analysis is None:
        raise HTTPException(404, "Analysis not found")
    return _serialize_analysis(analysis)


def delete_analysis(db: Session, *, analysis_id: UUID, user: User) -> None:
    """Delete an analysis owned by the user."""
    analysis = db.scalar(
        select(Analysis).where(
            Analysis.id == analysis_id, Analysis.user_id == user.id
        )
    )
    if analysis is None:
        raise HTTPException(404, "Analysis not found")
    db.delete(analysis)
    db.commit()


def get_admin_stats(db: Session) -> dict[str, Any]:
    """Admin stats for cost monitoring."""
    total = db.scalar(select(func.count(Analysis.id))) or 0
    fallback_count = db.scalar(
        select(func.count(Analysis.id)).where(Analysis.status == "fallback")
    ) or 0
    completed_count = db.scalar(
        select(func.count(Analysis.id)).where(Analysis.status == "completed")
    ) or 0
    total_tokens = db.scalar(
        select(func.coalesce(func.sum(Analysis.input_tokens), 0))
        + func.coalesce(func.sum(Analysis.output_tokens), 0)
    ) or 0
    avg_latency = db.scalar(select(func.avg(Analysis.latency_ms))) or 0.0

    seven_days_ago = datetime.now(UTC) - timedelta(days=7)
    recent_count = db.scalar(
        select(func.count(Analysis.id)).where(Analysis.created_at >= seven_days_ago)
    ) or 0

    return {
        "total_analyses": total,
        "completed": completed_count,
        "fallback": fallback_count,
        "fallback_rate": round(fallback_count / total, 4) if total else 0.0,
        "recent_7_days": recent_count,
        "total_tokens": int(total_tokens),
        "avg_latency_ms": round(float(avg_latency), 2),
    }
