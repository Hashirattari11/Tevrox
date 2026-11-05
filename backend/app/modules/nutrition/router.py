from fastapi import APIRouter

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.get("/")
def nutrition_placeholder() -> dict[str, str]:
    return {"message": "Nutrition endpoints are not implemented yet."}
