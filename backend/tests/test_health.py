from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.database.session import get_db
from app.main import app

@pytest.fixture
def client():
    # The context manager runs FastAPI's lifespan, which initializes MongoDB.
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def test_health_reports_connected_database(client: TestClient) -> None:
    database = MagicMock()
    app.dependency_overrides[get_db] = lambda: database

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["database"] == "connected"
    assert response.json()["status"] == "ok"
    database.execute.assert_called_once()


def test_health_reports_unreachable_database(client: TestClient) -> None:
    database = MagicMock()
    database.execute.side_effect = OperationalError("SELECT 1", {}, Exception("offline"))
    app.dependency_overrides[get_db] = lambda: database

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["database"] == "unreachable"
