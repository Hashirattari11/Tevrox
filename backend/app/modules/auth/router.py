from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.models import User
from app.database.session import get_db
from app.modules.auth import service
from app.modules.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])
Db = Annotated[Session, Depends(get_db)]


@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup(payload: SignupRequest, request: Request, db: Db) -> dict:
    return service.signup(db, payload, request)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Db) -> dict:
    return service.login(db, payload, request)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, request: Request, db: Db) -> dict:
    return service.refresh(db, payload.refresh_token, request)


@router.post("/logout", status_code=204)
def logout(payload: RefreshRequest, db: Db) -> Response:
    service.logout(db, payload.refresh_token)
    return Response(status_code=204)


@router.post("/logout-all", status_code=204)
def logout_all(user: Annotated[User, Depends(get_current_user)], db: Db) -> Response:
    service.logout_all(db, user)
    return Response(status_code=204)


@router.post("/change-password", status_code=204)
def change_password(
    payload: ChangePasswordRequest, user: Annotated[User, Depends(get_current_user)], db: Db
) -> Response:
    service.change_password(db, user, payload.current_password, payload.new_password)
    return Response(status_code=204)


@router.get("/me", response_model=UserResponse)
def me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user
