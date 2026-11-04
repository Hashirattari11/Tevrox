from fastapi import APIRouter

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/")
def products_placeholder() -> dict[str, str]:
    return {"message": "Product endpoints are not implemented yet."}
