"""Initial schema for users, product catalog, routines, and nutrition."""
from alembic import op

from app.database import models  # noqa: F401
from app.database.base import Base

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
