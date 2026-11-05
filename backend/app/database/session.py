from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

# Build engine; connect_args only for non-SQLite drivers
_database_url = get_settings().database_url
_sqlite_prefix = "sqlite"
connect_args = {"check_same_thread": False} if _database_url.startswith(_sqlite_prefix) else {"connect_timeout": 5}

engine = create_engine(
    _database_url,
    pool_pre_ping=True,
    connect_args=connect_args,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
