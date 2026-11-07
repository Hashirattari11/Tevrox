"""Phase 4 AI analysis: analyses table columns, ingredient safety fields.

Revision ID: 0004_phase4_ai_analysis
Revises: 0003_phase3_catalog
Create Date: 2026-11-07 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# Portable JSON: JSONB on PostgreSQL, generic JSON elsewhere (e.g. SQLite checks).
PortableJSONB = sa.JSON().with_variant(sa.JSON(), "postgresql")

revision: str = "0004_phase4_ai_analysis"
down_revision: str | None = "0003_phase3_catalog"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

# Portable enum: native on PostgreSQL, CHECK constraint elsewhere.
IrritationPotential = sa.Enum(
    "low", "moderate", "high", "unknown", name="irritation_potential"
)
AnalysisStatus = sa.Enum(
    "completed", "fallback", "failed", name="analysis_status"
)


def upgrade() -> None:
    # ---- analyses: add Phase 4 columns ----
    op.add_column(
        "analyses",
        sa.Column("prompt_version", sa.String(80), nullable=True),
    )
    op.add_column(
        "analyses",
        sa.Column("rules_version", sa.String(80), nullable=True),
    )
    op.add_column(
        "analyses",
        sa.Column("input_hash", sa.String(64), nullable=True, index=True),
    )
    op.add_column(
        "analyses",
        sa.Column(
            "status",
            AnalysisStatus,
            nullable=False,
            server_default="completed",
        ),
    )
    op.add_column(
        "analyses",
        sa.Column("latency_ms", sa.Integer(), nullable=True),
    )
    op.add_column(
        "analyses",
        sa.Column("input_tokens", sa.Integer(), nullable=True),
    )
    op.add_column(
        "analyses",
        sa.Column("output_tokens", sa.Integer(), nullable=True),
    )
    op.add_column(
        "analyses",
        sa.Column("error_code", sa.String(80), nullable=True),
    )

    # ---- ingredients: add Phase 4 safety columns ----
    op.add_column(
        "ingredients",
        sa.Column(
            "function_tags",
            PortableJSONB,
            nullable=True,
            server_default="[]",
            comment="Educational functional tags (e.g. humectant, fragrance, preservative)",
        ),
    )
    op.add_column(
        "ingredients",
        sa.Column("safety_notes", sa.Text(), nullable=True),
    )
    op.add_column(
        "ingredients",
        sa.Column(
            "irritation_potential",
            IrritationPotential,
            nullable=False,
            server_default="unknown",
        ),
    )


def downgrade() -> None:
    # Remove ingredient columns
    op.drop_column("ingredients", "irritation_potential")
    op.drop_column("ingredients", "safety_notes")
    op.drop_column("ingredients", "function_tags")

    # Remove analyses indexes (auto-created via index=True) then columns
    op.drop_index("ix_analyses_input_hash", table_name="analyses", if_exists=True)
    op.drop_column("analyses", "error_code")
    op.drop_column("analyses", "output_tokens")
    op.drop_column("analyses", "input_tokens")
    op.drop_column("analyses", "latency_ms")
    op.drop_column("analyses", "status")
    op.drop_column("analyses", "input_hash")
    op.drop_column("analyses", "rules_version")
    op.drop_column("analyses", "prompt_version")

    # Drop enums (PostgreSQL)
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS irritation_potential")
        op.execute("DROP TYPE IF EXISTS analysis_status")
