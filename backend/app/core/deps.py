from collections.abc import Callable
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.models import User
from app.database.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]
) -> User:
    try:
        claims = decode_access_token(token)
        user_id = UUID(claims["sub"])
    except (jwt.PyJWTError, ValueError, KeyError):
        raise HTTPException(
            401, "AUTH_TOKEN_INVALID", headers={"WWW-Authenticate": "Bearer"}
        ) from None
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None or not user.is_active:
        raise HTTPException(401, "AUTH_TOKEN_INVALID", headers={"WWW-Authenticate": "Bearer"})
    return user


def require_role(role: str) -> Callable:
    def dependency(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role.value != role:
            raise HTTPException(403, "AUTH_FORBIDDEN")
        return user

    return dependency
