from fastapi import APIRouter

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.get("/")
def ingredients_placeholder() -> dict[str, str]:
    return {"message": "Ingredient endpoints are not implemented yet."}
