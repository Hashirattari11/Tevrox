from collections.abc import Generator

from fastapi.testclient import TestClient

from app.database.session import get_db
from app.main import app


class UnavailableDatabase:
    def execute(self, _statement: object) -> None:
        raise ConnectionError("Database is unavailable")


def unavailable_db() -> Generator[UnavailableDatabase, None, None]:
    yield UnavailableDatabase()


def test_health_reports_database_status() -> None:
    app.dependency_overrides[get_db] = unavailable_db
    try:
        response = TestClient(app).get("/api/v1/health")
    finally:
        app.dependency_overrides.pop(get_db)
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "tevrox-backend",
        "version": "0.1.0",
        "database": "unreachable",
    }
