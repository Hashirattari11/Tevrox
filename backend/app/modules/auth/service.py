from datetime import UTC, datetime, timedelta
from typing import Any

from argon2 import PasswordHasher
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, generate_refresh_token, hash_refresh_token
from app.database.models import User, RefreshToken
from app.database.models import UserProfile
from app.modules.auth.schemas import UserResponse

_hasher = PasswordHasher()


# ─── Helpers ──────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return _hasher.verify(hashed, password)
    except Exception:
        return False


# ─── Signup ───────────────────────────────────────────────────────────────

def signup(db: Session, payload: Any, request: Any) -> dict[str, any]:
    """Create a new user + empty profile. Return user + tokens."""
    email = payload.email.strip().lower()
    # Check duplicate
    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(409, "AUTH_EMAIL_TAKEN")
    # Create user
    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # Create empty profile
    profile = UserProfile(user_id=user.id)
    db.add(profile)
    db.commit()
    # Create tokens
    access = create_access_token(user_id=str(user.id), role=user.role)
    refresh = generate_refresh_token()
    refresh_hash = hash_refresh_token(refresh)
    expires_at = datetime.now(UTC) + timedelta(
        days=get_settings().refresh_token_expire_days
    )
    rt = RefreshToken(
        user_id=user.id,
        token_hash=refresh_hash,
        family_id=user.id,
        expires_at=expires_at,
    )
    db.add(rt)
    db.commit()
    # Build user response
    user_response = UserResponse.model_validate(user)
    tokens = {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "user": user_response,
    }
    return tokens


# ─── Login ────────────────────────────────────────────────────────────────

def login(db: Session, payload: Any, request: Any) -> dict[str, any]:
    """Authenticate user. Return user + tokens. Updates last_login_at."""
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "AUTH_INVALID_CREDENTIALS")
    # Update last_login_at
    user.last_login_at = datetime.now(UTC)
    db.commit()
    # Create tokens
    access = create_access_token(user_id=str(user.id), role=user.role)
    refresh = generate_refresh_token()
    refresh_hash = hash_refresh_token(refresh)
    expires_at = datetime.now(UTC) + timedelta(
        days=get_settings().refresh_token_expire_days
    )
    rt = RefreshToken(
        user_id=user.id,
        token_hash=refresh_hash,
        family_id=user.id,
        expires_at=expires_at,
    )
    db.add(rt)
    db.commit()
    db.refresh(user)
    user_response = UserResponse.model_validate(user)
    tokens = {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "user": user_response,
    }
    return tokens


# ─── Refresh ──────────────────────────────────────────────────────────────

def refresh(
    db: Session, refresh_token: str, request: Any
) -> dict[str, any]:
    """Rotate refresh token. Return new access + new refresh token."""
    provided_hash = hash_refresh_token(refresh_token)
    rt = db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == provided_hash)
    )
    if rt is None or rt.revoked_at is not None:
        raise HTTPException(401, "AUTH_TOKEN_INVALID")
    if rt.expires_at < datetime.now(UTC):
        raise HTTPException(401, "AUTH_TOKEN_EXPIRED")
    # Revoke old token
    rt.revoked_at = datetime.now(UTC)
    db.commit()
    # Get user
    user = db.get(User, rt.user_id)
    # Generate new refresh token
    new_refresh = generate_refresh_token()
    new_refresh_hash = hash_refresh_token(new_refresh)
    new_expires = datetime.now(UTC) + timedelta(
        days=get_settings().refresh_token_expire_days
    )
    new_rt = RefreshToken(
        user_id=user.id,
        token_hash=new_refresh_hash,
        family_id=user.id,
        expires_at=new_expires,
    )
    db.add(new_rt)
    db.commit()
    # Create new access token
    access = create_access_token(user_id=str(user.id), role=user.role)
    user_response = UserResponse.model_validate(user)
    tokens = {
        "access_token": access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "user": user_response,
    }
    return tokens


# ─── Logout ───────────────────────────────────────────────────────────────

def logout(db: Session, refresh_token: str) -> None:
    """Revoke the supplied refresh token."""
    provided_hash = hash_refresh_token(refresh_token)
    rt = db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == provided_hash)
    )
    if rt is not None:
        rt.revoked_at = datetime.now(UTC)
        db.commit()


# ─── Logout-All ───────────────────────────────────────────────────────────

def logout_all(db: Session, user: User) -> None:
    """Revoke all refresh tokens of the current user."""
    db.execute(
        RefreshToken.__table__.update()
        .where(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
    )
    db.commit()


# ─── Change-Password ──────────────────────────────────────────────────────

def change_password(
    db: Session, user: User, current_password: str, new_password: str
) -> None:
    """Verify current password, hash new one, revoke all other refresh tokens."""
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(401, "AUTH_INVALID_CREDENTIALS")
    # Update password
    user.password_hash = hash_password(new_password)
    db.commit()
    # Revoke all refresh tokens
    logout_all(db, user)


# ─── Me ───────────────────────────────────────────────────────────────────

def me(user: Any) -> User:
    return user  # user already injected by dependency