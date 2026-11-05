from fastapi import APIRouter

router = APIRouter(prefix="/conflicts", tags=["conflicts"])


@router.get("/")
def conflicts_placeholder() -> dict[str, str]:
    return {"message": "Conflict endpoints are not implemented yet."}
