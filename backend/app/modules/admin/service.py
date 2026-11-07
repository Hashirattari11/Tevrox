"""Business logic for administrative workflows."""

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException

from app.database.models import AdminAuditLog, Ingredient, Product, User, UserProfile


def get_stats_overview(db_session) -> dict[str, Any]:
    """Get admin dashboard statistics overview."""

    # Total products
    total_products = db_session.query(Product).filter(Product.is_active.is_(True)).count()

    # Verification status counts
    verified_count = db_session.query(Product).filter(
        Product.is_active.is_(True), Product.verification_status == "verified"
    ).count()
    unverified_count = db_session.query(Product).filter(
        Product.is_active.is_(True), Product.verification_status == "unverified"
    ).count()
    rejected_count = db_session.query(Product).filter(
        Product.is_active.is_(True), Product.verification_status == "rejected"
    ).count()

    # Users
    total_users = db_session.query(User).count()
    active_users = db_session.query(User).filter(User.is_active.is_(True)).count()

    # Ingredients
    total_ingredients = db_session.query(Ingredient).count()
    unreviewed_ingredients = db_session.query(Ingredient).filter(
        Ingredient.is_reviewed.is_(False)
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

    start_date = datetime.now(UTC) - timedelta(days=days)

    # Query signup data - we'll use a simplified approach
    # In a real implementation, this would track signups with timestamps
    signup_date = func.date(User.created_at)
    daily_counts = (
        db_session.query(
            signup_date.label("date"), func.count(User.id).label("count")
        )
        .filter(User.created_at >= start_date)
        .group_by(signup_date)
        .order_by(signup_date)
        .all()
    )

    # Fill in missing days with 0
    result = []
    date_map = {str(row.date): row.count for row in daily_counts}

    for i in range(days):
        date = (datetime.now(UTC) - timedelta(days=days - 1 + i)).strftime("%Y-%m-%d")
        result.append({"date": date, "count": date_map.get(date, 0)})

    return result


def get_users(
    db_session,
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
    active_only: bool = True,
) -> tuple[list[dict[str, Any]], int]:
    """Get users with search and pagination."""
    from sqlalchemy import func, or_, select

    query = select(User).outerjoin(UserProfile, UserProfile.user_id == User.id)
    count_query = select(func.count(User.id)).outerjoin(
        UserProfile, UserProfile.user_id == User.id
    )

    if search:
        condition = or_(
            User.email.ilike(f"%{search}%"),
            UserProfile.full_name.ilike(f"%{search}%"),
        )
        query = query.filter(condition)
        count_query = count_query.filter(condition)

    if active_only:
        query = query.filter(User.is_active.is_(True))
        count_query = count_query.filter(User.is_active.is_(True))

    total = db_session.execute(count_query).scalar_one()

    rows = db_session.execute(
        query.add_columns(UserProfile.full_name).offset(skip).limit(limit)
    ).all()

    return [
        {
            "id": str(user.id),
            "email": user.email,
            "name": full_name or "",
            "role": str(user.role),
            "active": user.is_active,
            "created": user.created_at.isoformat() if user.created_at else None,
            "lastLogin": user.last_login_at.isoformat() if user.last_login_at else None,
        }
        for user, full_name in rows
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
        before_summary="User was active",
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
        before_summary="User was inactive",
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
    from sqlalchemy import func, select

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
        db_session.execute(
            query.order_by(AdminAuditLog.created_at.desc()).offset(skip).limit(limit)
        )
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
    from app.database.models import AdminAuditLog

    if len(product_ids) > 100:
        raise HTTPException(400, "Maximum 100 product IDs per bulk request")

    # Get the products
    from sqlalchemy import select

    products = (
        db_session.execute(select(Product).where(Product.id.in_(product_ids)))
        .scalars()
        .all()
    )

    if len(products) != len(product_ids):
        raise HTTPException(404, "Some products not found")

    now = datetime.now(UTC)

    for product in products:
        before_status = product.verification_status
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
            entity_id=product.id,
            before_summary=f"status was '{before_status}'",
            after_summary=f"status is '{product.verification_status}'",
            admin_user_id=current_user.id,
        )
        db_session.add(audit)

    db_session.commit()

    return {
        "message": f"{action.title()}d {len(products)} product(s) successfully",
    }
