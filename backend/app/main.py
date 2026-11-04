from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.database.session import get_db
from app.modules import (
    admin,
    analysis,
    auth,
    conflicts,
    ingredients,
    nutrition,
    products,
    routines,
    users,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

configure_logging()
settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)

api_v1 = APIRouter(prefix="/api/v1")


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    database: str


@api_v1.get("/health", response_model=HealthResponse, tags=["system"])
def health(db: Annotated[Session, Depends(get_db)]) -> HealthResponse:
    database = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        database = "unreachable"
    return HealthResponse(
        status="ok",
        service="tevrox-backend",
        version=settings.app_version,
        database=database,
    )


for module in (auth, users, products, ingredients, analysis, conflicts, routines, nutrition, admin):
    api_v1.include_router(module.router.router)

app.include_router(api_v1)
