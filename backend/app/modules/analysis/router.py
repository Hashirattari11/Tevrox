"""Analysis API routes (Phase 4).

Endpoints under /api/v1/analysis, all authenticated.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.models import User
from app.database.session import get_db
from app.modules.analysis import service
from app.modules.analysis.schemas import AnalysisCreate, AnalysisResponse

router = APIRouter(prefix="/analysis", tags=["analysis"])
Db = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("", response_model=AnalysisResponse, status_code=201)
def create_analysis(
    payload: AnalysisCreate,
    db: Db,
    user: CurrentUser,
    force_refresh: bool = Query(
        False, description="Force a fresh analysis (rate-limited)"
    ),
) -> AnalysisResponse:
    """Run ingredient analysis for a product."""
    result = service.run_analysis(
        db, user=user, product_id=payload.product_id, force_refresh=force_refresh
    )
    return AnalysisResponse.model_validate(result)


@router.get("", response_model=dict)
def list_analyses(
    db: Db,
    user: CurrentUser,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict:
    """Current user's analysis history, newest first."""
    items, total = service.get_analysis_history(
        db, user=user, limit=limit, offset=offset
    )
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: UUID,
    db: Db,
    user: CurrentUser,
) -> AnalysisResponse:
    """Get a single analysis (owner only)."""
    result = service.get_analysis_by_id(db, analysis_id=analysis_id, user=user)
    return AnalysisResponse.model_validate(result)


@router.delete("/{analysis_id}", status_code=204)
def delete_analysis(
    analysis_id: UUID,
    db: Db,
    user: CurrentUser,
) -> None:
    """Delete an analysis owned by the current user."""
    service.delete_analysis(db, analysis_id=analysis_id, user=user)


@router.get("/admin/stats", response_model=dict)
def admin_analysis_stats(
    db: Db,
    user: CurrentUser,
) -> dict:
    """Admin-only: analysis cost/usage stats."""
    if user.role != "admin":
        raise HTTPException(403, "AUTH_FORBIDDEN")
    return service.get_admin_stats(db)
