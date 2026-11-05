"""Business logic for administrative workflows."""

from typing import Any, Optional
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from app.core.deps import get_db, get_current_user
from app.database.models import Product, User, AdminAuditLog, Ingredient
from app.database.session import get_db as get_db_session


def get_stats_overview(db_session) -> dict[str, Any]:
    """Get admin dashboard statistics overview."""
    from sqlalchemy import func

    # Total products
    total_products = db_session.query(Product).filter(Product.is_active == True).count()

    # Verification status counts
    verified_count = db_session.query(Product).filter(
        Product.is_active == True, Product.verification_status == "verified"
    ).count()
    unverified_count = db_session.query(Product).filter(
        Product.is_active == True, Product.verification_status == "unverified"
    ).count()
    rejected_count = db_session.query(Product).filter(
        Product.is_active == True, Product.verification_status == "rejected"
    ).count()

    # Users
    total_users = db_session.query(User).count()
    active_users = db_session.query(User).filter(User.is_active == True).count()

    # Ingredients
    total_ingredients = db_session.query(Ingredient).count()
    unreviewed_ingredients = db_session.query(Ingredient).filter(
        Ingredient.category_function == "other"
    ).count()

    # Recent activity count
    recent_activity = db_session.query(AdminAuditLog).count()

    return {
        "totalProducts": total_products,
        "verifiedProducts": verified_count,
        "unverifiedProducts": unverified_count,
        "rejectedProducts": rejected_count,
        "totalUsers": total_users,
        "activeUsers": active_users,
        "totalIngredients": total_ingredients,
        "unreviewedIngredients": unreviewed_ingredients,
        "pendingReviewItems": unverified_count,
        "recentActivity": recent_activity,
    }


def get_signups_stats(db_session, days: int = 30) -> list[dict[str, Any]]:
    """Get daily signup counts for the specified number of days."""
    from sqlalchemy import func

    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    # Query signup data - we'll use a simplified approach
    # In a real implementation, this would track signups with timestamps
    daily_counts = (
        db_session.query(func.date(User.created_at).label("date"), func.count(User.id).label("count"))
        .filter(User.created_at >= start_date)
        .group_by(func.date(User.created_at))
        .order_by(func.date(User.created_at))
        .all()
    )

    # Fill in missing days with 0
    result = []
    date_map = {str(row.date): row.count for row in daily_counts}

    for i in range(days):
        date = (datetime.now(timezone.utc) - timedelta(days=days - 1 + i)).strftime("%Y-%m-%d")
        result.append({
            "date": date,
            "count": date_map.get(date, 0),
        })

    return result


def get_users(
    db_session,
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
    active_only: bool = True,
) -> tuple[list[dict[str, Any]], int]:
    """Get users with search and pagination."""
    from sqlalchemy import select, func, or_

    query = select(User)
    count_query = select(func.count(User.id))

    if search:
        query = query.filter(
            or_(
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
            )
        )
        count_query = count_query.filter(
            or_(
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
            )
        )

    if active_only:
        query = query.filter(User.is_active == True)
        count_query = count_query.filter(User.is_active == True)

    total = db_session.execute(count_query).scalar_one()

    users = db_session.execute(query.offset(skip).limit(limit)).scalars().all()

    return [
        {
            "id": str(user.id),
            "email": user.email,
            "name": user.full_name or "",
            "role": "admin" if user.is_active else "user",
            "active": user.is_active,
            "created": user.created_at.isoformat() if user.created_at else None,
            "lastLogin": user.last_login_at.isoformat() if user.last_login_at else None,
        }
        for user in users
    ], total


def deactivate_user(db_session, user_id: str, current_user: User) -> dict[str, Any]:
    """Deactivate a user (revokes all refresh tokens)."""
    from sqlalchemy import update

    # Prevent self-deactivation
    if user_id == str(current_user.id):
        raise HTTPException(400, "Cannot deactivate yourself")

    # Deactivate the user
    db_session.execute(
        update(User).where(User.id == user_id).values(is_active=False)
    )

    # Create audit log
    from app.database.models import AdminAuditLog

    audit = AdminAuditLog(
        action="user_deactivate",
        entity_type="user",
        entity_id=user_id,
        before_summary=f"User was active",
        admin_user_id=current_user.id,
    )
    db_session.add(audit)
    db_session.commit()

    return {"message": "User deactivated successfully"}


def reactivate_user(db_session, user_id: str, current_user: User) -> dict[str, Any]:
    """Reactivate a user."""
    from sqlalchemy import update

    db_session.execute(
        update(User).where(User.id == user_id).values(is_active=True)
    )

    # Create audit log
    from app.database.models import AdminAuditLog

    audit = AdminAuditLog(
        action="user_reactivate",
        entity_type="user",
        entity_id=user_id,
        before_summary=f"User was inactive",
        admin_user_id=current_user.id,
    )
    db_session.add(audit)
    db_session.commit()

    return {"message": "User reactivated successfully"}


def get_audit_logs(
    db_session,
    actor_id: str | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[dict[str, Any]], int]:
    """Get audit logs with filters and pagination."""
    from sqlalchemy import select, func

    query = select(AdminAuditLog)
    count_query = select(func.count(AdminAuditLog.id))

    if actor_id:
        query = query.filter(AdminAuditLog.admin_user_id == actor_id)
        count_query = count_query.filter(AdminAuditLog.admin_user_id == actor_id)

    if action:
        query = query.filter(AdminAuditLog.action == action)
        count_query = count_query.filter(AdminAuditLog.action == action)

    if entity_type:
        query = query.filter(AdminAuditLog.entity_type == entity_type)
        count_query = count_query.filter(AdminAuditLog.entity_type == entity_type)

    if date_from:
        query = query.filter(AdminAuditLog.created_at >= date_from)
        count_query = count_query.filter(AdminAuditLog.created_at >= date_from)

    if date_to:
        query = query.filter(AdminAuditLog.created_at <= date_to)
        count_query = count_query.filter(AdminAuditLog.created_at <= date_to)

    total = db_session.execute(count_query).scalar_one()

    logs = (
        db_session.execute(query.order_by(AdminAuditLog.created_at.desc()).offset(skip).limit(limit))
        .scalars()
        .all()
    )

    return [
        {
            "id": str(log.id),
            "actor": str(log.admin_user_id) if log.admin_user_id else "system",
            "action": log.action,
            "entityType": log.entity_type,
            "entityId": str(log.entity_id) if log.entity_id else None,
            "beforeSummary": log.before_summary,
            "afterSummary": log.after_summary,
            "createdAt": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ], total


def bulk_product_action(
    db_session,
    product_ids: list[str],
    action: str,
    current_user: User,
) -> dict[str, Any]:
    """Bulk verify or reject products."""
    from sqlalchemy import update
    from app.database.models import AdminAuditLog

    if len(product_ids) > 100:
        raise HTTPException(400, "Maximum 100 product IDs per bulk request")

    # Get the products
    from sqlalchemy import select
    products = db_session.execute(
        select(Product).where(Product.id.in_(product_ids))
    ).scalars().all()

    if len(products) != len(product_ids):
        raise HTTPException(404, "Some products not found")

    now = datetime.now(timezone.utc)

    for product in products:
        # Update verification status
        if action == "verify":
            product.verification_status = "verified"
            product.verified_by = current_user.id
            product.verified_at = now
        elif action == "reject":
            product.verification_status = "rejected"

        # Create audit log
        audit = AdminAuditLog(
            action=f"product_{action}",
            entity_type="product",
            entity_id=str(product.id),
            before_summary=f"status was '{product.verification_status}'",
            after_summary=f"status is '{product.verification_status}'",
            admin_user_id=current_user.id,
        )
        db_session.add(audit)

    db_session.commit()

    return {
        "message": f"{action.title()}d {len(products)} product(s) successfully",
    }
