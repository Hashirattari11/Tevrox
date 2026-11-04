from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/")
def auth_placeholder() -> dict[str, str]:
    return {"message": "Authentication will be implemented in Weeks 2–3."}
