from fastapi import APIRouter

router = APIRouter(prefix="/routines", tags=["routines"])


@router.get("/")
def placeholder() -> dict[str, str]:
    return {"message": "Routine endpoints are planned."}
