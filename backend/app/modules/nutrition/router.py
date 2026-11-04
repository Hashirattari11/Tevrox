from fastapi import APIRouter

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.get("/")
def placeholder() -> dict[str, str]:
    return {"message": "Nutrition endpoints are planned."}
