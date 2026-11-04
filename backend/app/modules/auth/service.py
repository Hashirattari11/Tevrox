import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.database.models import RefreshToken, User, UserProfile
from app.modules.auth.schemas import LoginRequest, SignupRequest


def _issue(db: Session, user: User, request: Request, family_id: uuid.UUID | None = None) -> dict:
    raw = generate_refresh_token()
    row = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw),
        family_id=family_id or uuid.uuid4(),
        expires_at=datetime.now(UTC) + timedelta(days=get_settings().refresh_token_expire_days),
        user_agent=request.headers.get("user-agent", "")[:512] or None,
        ip_address=request.client.host if request.client else None,
    )
    db.add(row)
    db.flush()
    return {
        "access_token": create_access_token(str(user.id), user.role.value),
        "refresh_token": raw,
        "token_type": "bearer",
        "user": user,
    }


def signup(db: Session, payload: SignupRequest, request: Request) -> dict:
    if db.scalar(select(User.id).where(User.email == payload.email)):
        raise HTTPException(409, "AUTH_EMAIL_TAKEN")
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()
    db.add(
        UserProfile(user_id=user.id, full_name=payload.full_name, skin_concerns=[], preferences={})
    )
    result = _issue(db, user, request)
    db.commit()
    return result


def login(db: Session, payload: LoginRequest, request: Request) -> dict:
    user = db.scalar(select(User).where(User.email == payload.email))
    # Always verify a real hash where possible; callers receive the same failure either way.
    valid = user is not None and verify_password(payload.password, user.password_hash)
    if not valid or user is None or not user.is_active:
        raise HTTPException(401, "AUTH_INVALID_CREDENTIALS")
    user.last_login_at = datetime.now(UTC)
    result = _issue(db, user, request)
    db.commit()
    return result


def refresh(db: Session, raw: str, request: Request) -> dict:
    row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(raw)))
    now = datetime.now(UTC)
    if row is None:
        raise HTTPException(401, "AUTH_TOKEN_INVALID")
    if row.revoked_at is not None:
        if row.replaced_by is not None:
            db.execute(
                update(RefreshToken)
                .where(RefreshToken.family_id == row.family_id)
                .values(revoked_at=now)
            )
            db.commit()
        raise HTTPException(401, "AUTH_TOKEN_INVALID")
    if row.expires_at <= now:
        row.revoked_at = now
        db.commit()
        raise HTTPException(401, "AUTH_TOKEN_EXPIRED")
    user = db.get(User, row.user_id)
    if user is None or not user.is_active:
        raise HTTPException(401, "AUTH_TOKEN_INVALID")
    result = _issue(db, user, request, row.family_id)
    replacement = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(result["refresh_token"])
        )
    )
    row.revoked_at = now
    row.replaced_by = replacement.id if replacement else None
    db.commit()
    return result


def logout(db: Session, raw: str) -> None:
    row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(raw)))
    if row and row.revoked_at is None:
        row.revoked_at = datetime.now(UTC)
        db.commit()


def logout_all(db: Session, user: User) -> None:
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
    )
    db.commit()


def change_password(db: Session, user: User, current: str, new: str) -> None:
    if not verify_password(current, user.password_hash):
        raise HTTPException(401, "AUTH_INVALID_CREDENTIALS")
    user.password_hash = hash_password(new)
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
    )
    db.commit()
