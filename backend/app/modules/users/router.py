from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
def users_placeholder() -> dict[str, str]:
    return {"message": "User endpoints are not implemented yet."}
