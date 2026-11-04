from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.database.models import RefreshToken, User, UserProfile
from app.modules.users.schemas import ProfileUpdate


def get_profile(db: Session, user: User) -> UserProfile:
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    if profile is None:
        raise HTTPException(404, "Profile not found")
    return profile


def update_profile(db: Session, user: User, payload: ProfileUpdate) -> UserProfile:
    profile = get_profile(db, user)
    for field, value in payload.model_dump().items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


def deactivate(db: Session, user: User) -> None:
    user.is_active = False
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
    )
    db.commit()
