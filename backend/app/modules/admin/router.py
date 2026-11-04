from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/")
def placeholder() -> dict[str, str]:
    return {"message": "Administrative endpoints are planned."}
