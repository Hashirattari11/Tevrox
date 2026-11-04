from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import AsyncMongoClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.database.mongodb import MongoStatus, get_mongodb_status
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
    mongodb: MongoStatus


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


for module in (auth, users, products, ingredients, analysis, conflicts, routines, nutrition, admin):
    api_v1.include_router(module.router.router)

app.include_router(api_v1)
