from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.database.models import User
from app.database.session import get_db as get_db_session
from app.modules.admin.schemas import (
    AdminActionResponse,
    AdminAuditLogsListResponse,
    AdminBulkActionResponse,
    AdminBulkProductActionRequest,
    AdminSignupsStatsResponse,
    AdminStatsOverviewResponse,
    AdminUsersListResponse,
)
from app.modules.admin.service import (
    bulk_product_action,
    deactivate_user,
    get_audit_logs,
    get_signups_stats,
    get_stats_overview,
    get_users,
    reactivate_user,
)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_role("admin"))],
)
Db = Annotated[Session, Depends(get_db_session)]
AdminUser = Annotated[User, Depends(require_role("admin"))]


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


@router.get("/stats/overview", response_model=AdminStatsOverviewResponse)
def admin_stats_overview(db: Db) -> dict:
    """Get admin dashboard statistics overview."""
    return get_stats_overview(db)


@router.get("/stats/signups", response_model=AdminSignupsStatsResponse)
def admin_stats_signups(
    db: Db,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
) -> dict:
    """Get daily signup counts."""
    return get_signups_stats(db, days)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


@router.get("/users", response_model=AdminUsersListResponse)
def admin_users_list(
    db: Db,
    _actor: AdminUser,
    search: str | None = Query(
        None, min_length=1, max_length=200, description="Search by email or name"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum records to return"),
    active_only: bool = Query(True, description="Show only active users"),
) -> dict:
    """List users with search and pagination."""
    users, total = get_users(db, search, skip, limit, active_only)
    return {"users": users, "total": total, "skip": skip, "limit": limit}


@router.post("/users/{user_id}/deactivate", response_model=AdminActionResponse)
def admin_user_deactivate(
    user_id: str,
    db: Db,
    actor: AdminUser,
) -> dict:
    """Deactivate a user (revokes all refresh tokens)."""
    return deactivate_user(db, user_id, actor)


@router.post("/users/{user_id}/reactivate", response_model=AdminActionResponse)
def admin_user_reactivate(
    user_id: str,
    db: Db,
    actor: AdminUser,
) -> dict:
    """Reactivate a user."""
    return reactivate_user(db, user_id, actor)


# ---------------------------------------------------------------------------
# Audit logs
# ---------------------------------------------------------------------------


@router.get("/audit-logs", response_model=AdminAuditLogsListResponse)
def admin_audit_logs(
    db: Db,
    _actor: AdminUser,
    actor_id: str | None = Query(None, description="Filter by actor user ID"),
    action: str | None = Query(None, description="Filter by action type"),
    entity_type: str | None = Query(None, description="Filter by entity type"),
    date_from: str | None = Query(None, description="Start date (ISO format)"),
    date_to: str | None = Query(None, description="End date (ISO format)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum records to return"),
) -> dict:
    """Get audit logs with filters and pagination."""
    logs, total = get_audit_logs(
        db, actor_id, action, entity_type, date_from, date_to, skip, limit
    )
    return {"logs": logs, "total": total, "skip": skip, "limit": limit}


# ---------------------------------------------------------------------------
# Products bulk actions
# ---------------------------------------------------------------------------


@router.post("/products/bulk-verify", response_model=AdminBulkActionResponse)
def admin_products_bulk_verify(
    payload: AdminBulkProductActionRequest,
    db: Db,
    actor: AdminUser,
) -> dict:
    """Bulk verify products (max 100 IDs)."""
    return bulk_product_action(db, payload.product_ids, "verify", actor)


@router.post("/products/bulk-reject", response_model=AdminBulkActionResponse)
def admin_products_bulk_reject(
    payload: AdminBulkProductActionRequest,
    db: Db,
    actor: AdminUser,
) -> dict:
    """Bulk reject products (max 100 IDs)."""
    return bulk_product_action(db, payload.product_ids, "reject", actor)
