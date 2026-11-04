from fastapi import APIRouter

router = APIRouter(prefix="/conflicts", tags=["conflicts"])


@router.get("/")
def placeholder() -> dict[str, str]:
    return {"message": "Ingredient conflict endpoints are planned."}
