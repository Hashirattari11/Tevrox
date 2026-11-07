from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token
from app.database.models import User
from app.database.session import Session, get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
_UNAUTHORIZED = {"WWW-Authenticate": "Bearer"}


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Validate bearer access token, load user, reject inactive users."""
    try:
        claims = decode_access_token(token)
        subject = UUID(str(claims.get("sub")))
    except Exception:
        raise HTTPException(
            401, "AUTH_TOKEN_INVALID", headers=_UNAUTHORIZED
        ) from None
    user = db.get(User, subject)
    if user is None:
        raise HTTPException(401, "AUTH_TOKEN_INVALID", headers=_UNAUTHORIZED)
    if not user.is_active:
        raise HTTPException(401, "AUTH_TOKEN_INVALID", headers=_UNAUTHORIZED)
    return user


def require_role(role: str) -> Callable:
    """Dependency factory: return a dependency that rejects non-admin users."""

    async def dependency(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role != role:
            raise HTTPException(403, "AUTH_FORBIDDEN")
        return user

    return dependency