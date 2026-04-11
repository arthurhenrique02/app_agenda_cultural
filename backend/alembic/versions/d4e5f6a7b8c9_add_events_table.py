"""add_events_table

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-04-11 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: str | Sequence[str] | None = "c3d4e5f6a7b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create events table."""
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("venue_name", sa.String(length=200), nullable=False),
        sa.Column("address", sa.String(length=300), nullable=False),
        sa.Column("neighborhood", sa.String(length=100), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pendente",
                "aprovado",
                "rejeitado",
                "cancelado",
                name="eventstatus",
            ),
            nullable=False,
            server_default="pendente",
        ),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("reviewed_by", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_events_status"), "events", ["status"], unique=False)
    op.create_index(op.f("ix_events_date"), "events", ["date"], unique=False)
    op.create_index(
        op.f("ix_events_category_id"), "events", ["category_id"], unique=False
    )
    op.create_index(
        op.f("ix_events_created_by"), "events", ["created_by"], unique=False
    )


def downgrade() -> None:
    """Drop events table."""
    op.drop_index(op.f("ix_events_created_by"), table_name="events")
    op.drop_index(op.f("ix_events_category_id"), table_name="events")
    op.drop_index(op.f("ix_events_date"), table_name="events")
    op.drop_index(op.f("ix_events_status"), table_name="events")
    op.drop_table("events")
    op.execute("DROP TYPE IF EXISTS eventstatus")
