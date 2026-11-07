"""Shared pytest fixtures for the Tevrox backend.

Environment variables are set before importing the application so the global
engine never points at a real PostgreSQL instance during tests.
"""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./_pytest_app.db"
os.environ["JWT_SECRET"] = "test-secret-at-least-thirty-two-characters"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000"
os.environ["PRODUCT_SUBMISSION_RATE_LIMIT"] = "3"
os.environ["PRODUCT_SUBMISSION_RATE_WINDOW_SECONDS"] = "600"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base
from app.database.models import User, UserProfile
from app.database.session import get_db
from app.integrations.product_provider import set_product_provider
from app.main import app
from app.modules.auth.service import hash_password
from app.modules.products.service import clear_submission_rate_limits

ADMIN_EMAIL = "admin@example.com"
USER_EMAIL = "user@example.com"
PASSWORD = "password123"


@pytest.fixture()
def session_factory(tmp_path: Path) -> Generator[sessionmaker[Session], None, None]:
    """Create a fresh SQLite database for each test."""
    engine = create_engine(
        f"sqlite:///{tmp_path / 'tevrox_test.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    yield factory
    engine.dispose()


@pytest.fixture()
def db_session(
    session_factory: sessionmaker[Session],
) -> Generator[Session, None, None]:
    with session_factory() as session:
        yield session


@pytest.fixture()
def client(session_factory: sessionmaker[Session]) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_process_state() -> Generator[None, None, None]:
    """Reset in-memory rate limits and the provider singleton per test."""
    clear_submission_rate_limits()
    set_product_provider(None)
    yield
    clear_submission_rate_limits()
    set_product_provider(None)


def _token_from_signup(client: TestClient, email: str, full_name: str) -> str:
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": PASSWORD, "full_name": full_name},
    )
    assert response.status_code == 201, response.text
    return response.json()["access_token"]


@pytest.fixture()
def user_token(client: TestClient) -> str:
    return _token_from_signup(client, USER_EMAIL, "Test User")


@pytest.fixture()
def admin_token(
    client: TestClient, session_factory: sessionmaker[Session]
) -> str:
    with session_factory() as session:
        admin = User(
            email=ADMIN_EMAIL,
            password_hash=hash_password(PASSWORD),
            role="admin",
        )
        session.add(admin)
        session.commit()
        session.add(UserProfile(user_id=admin.id, full_name="Test Admin"))
        session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": ADMIN_EMAIL, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
