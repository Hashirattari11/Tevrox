import logging
from typing import Annotated, Any, Literal

from fastapi import Depends, Request
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)
MongoStatus = Literal["connected", "unreachable"]


def get_mongo_client(request: Request) -> AsyncMongoClient[dict[str, Any]]:
    """Return the event-loop-scoped client created by the app lifespan."""
    return request.app.state.mongo_client


def get_mongo_database(request: Request) -> Any:
    """Return Tevrox's MongoDB database for application collections."""
    return request.app.state.mongo_database


async def get_mongodb_status(
    client: Annotated[AsyncMongoClient[dict[str, Any]], Depends(get_mongo_client)],
) -> MongoStatus:
    """Ping MongoDB for health reporting without failing the health route."""
    try:
        await client.admin.command("ping")
    except PyMongoError:
        logger.warning("MongoDB health check failed")
        return "unreachable"
    return "connected"
