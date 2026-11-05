from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import AsyncMongoClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.database.mongodb import MongoStatus, get_mongodb_status
from app.database.session import get_db
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.products.router import router as products_router
from app.modules.ingredients.router import router as ingredients_router
from app.modules.analysis.router import router as analysis_router
from app.modules.conflicts.router import router as conflicts_router
from app.modules.routines.router import router as routines_router
from app.modules.nutrition.router import router as nutrition_router
from app.modules.admin.router import router as admin_router

configure_logging()
settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    client: AsyncMongoClient[dict[str, Any]] = AsyncMongoClient(
        settings.mongodb_url,
        serverSelectionTimeoutMS=1500,
        connectTimeoutMS=1000,
    )
    application.state.mongo_client = client
    application.state.mongo_database = client.get_database(settings.mongodb_database)
    try:
        yield
    finally:
        await client.close()


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
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
    mongodb: str


@api_v1.get("/health", response_model=HealthResponse, tags=["system"])
def health(
    db: Annotated[Session, Depends(get_db)],
    mongodb: Annotated[MongoStatus, Depends(get_mongodb_status)],
) -> HealthResponse:
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
        mongodb=mongodb,
    )


# Include each router (each router already defines its own prefix)
api_v1.include_router(auth_router, tags=["auth"])
api_v1.include_router(users_router, tags=["users"])
api_v1.include_router(products_router, tags=["products"])
api_v1.include_router(ingredients_router, tags=["ingredients"])
api_v1.include_router(analysis_router, tags=["analysis"])
api_v1.include_router(conflicts_router, tags=["conflicts"])
api_v1.include_router(routines_router, tags=["routines"])
api_v1.include_router(nutrition_router, tags=["nutrition"])
api_v1.include_router(admin_router, tags=["admin"])

app.include_router(api_v1)