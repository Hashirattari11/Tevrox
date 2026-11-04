from fastapi import APIRouter

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/")
def placeholder() -> dict[str, str]:
    return {"message": "Analysis endpoints are planned; no analysis is performed yet."}
