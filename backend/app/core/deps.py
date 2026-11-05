from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token
from app.database.models import User
from app.database.session import get_db, Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Annotated[User, Depends]:
    """Validate bearer access token, load user, reject inactive users."""
    try:
        claims = decode_access_token(token)
    except Exception:
        raise HTTPException(401, "AUTH_TOKEN_INVALID", headers={"WWW-Authenticate": "Bearer"}) from None
    user = db.get(User, claims.get("sub"))
    if user is None:
        raise HTTPException(401, "AUTH_TOKEN_INVALID", headers={"WWW-Authenticate": "Bearer"})
    if not user.is_active:
        raise HTTPException(401, "AUTH_TOKEN_INVALID", headers={"WWW-Authenticate": "Bearer"})
    return user


def require_role(role: str) -> Callable:
    """Dependency factory: return a dependency that rejects non-admin users."""
    async def dependency(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role != role:
            raise HTTPException(403, "AUTH_FORBIDDEN")
        return user
    return dependency