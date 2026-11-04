import os
from collections.abc import Generator

from fastapi.testclient import TestClient

from app.database.mongodb import get_mongodb_status

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET", "test-secret-which-is-at-least-thirty-two-characters")

from app.database.session import get_db
from app.main import app


class UnavailableDatabase:
    def execute(self, _statement: object) -> None:
        raise ConnectionError("Database is unavailable")


def unavailable_db() -> Generator[UnavailableDatabase, None, None]:
    yield UnavailableDatabase()


def test_health_reports_database_status() -> None:
    app.dependency_overrides[get_db] = unavailable_db
    app.dependency_overrides[get_mongodb_status] = lambda: "unreachable"
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/health")
    finally:
        app.dependency_overrides.pop(get_db)
        app.dependency_overrides.pop(get_mongodb_status)
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "tevrox-backend",
        "version": "0.1.0",
        "database": "unreachable",
        "mongodb": "unreachable",
    }
