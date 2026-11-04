from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.database.models import User
from app.database.session import get_db
from app.modules.users import service
from app.modules.users.schemas import ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/users", tags=["users"])
Db = Annotated[Session, Depends(get_db)]


@router.get("/me/profile", response_model=ProfileResponse)
def get_profile(user: Annotated[User, Depends(get_current_user)], db: Db):
    return service.get_profile(db, user)


@router.put("/me/profile", response_model=ProfileResponse)
def update_profile(
    payload: ProfileUpdate, user: Annotated[User, Depends(get_current_user)], db: Db
):
    return service.update_profile(db, user, payload)


@router.delete("/me", status_code=204)
def delete_account(user: Annotated[User, Depends(get_current_user)], db: Db):
    service.deactivate(db, user)
    return None


@router.get("/admin/ping", dependencies=[Depends(require_role("admin"))])
def admin_ping() -> dict[str, str]:
    return {"status": "ok"}
