from fastapi import APIRouter

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/")
def analysis_placeholder() -> dict[str, str]:
    return {"message": "Analysis endpoints are not implemented yet."}
