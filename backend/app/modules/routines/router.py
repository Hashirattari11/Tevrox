from fastapi import APIRouter

router = APIRouter(prefix="/routines", tags=["routines"])


@router.get("/")
def routines_placeholder() -> dict[str, str]:
    return {"message": "Routine endpoints are not implemented yet."}
