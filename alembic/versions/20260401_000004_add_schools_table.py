"""Add schools table

Revision ID: 20260401_000004
Revises: 20260401_000003
Create Date: 2026-04-01 00:10:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260401_000004"
down_revision: Union[str, None] = "20260401_000003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create schools table
    op.create_table(
        "schools",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("school_name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("pincode", sa.String(length=20), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("device_id", sa.String(length=255), nullable=True),
        sa.Column("last_synced_at", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_schools_id"), "schools", ["id"], unique=False)


def downgrade() -> None:
    # Drop schools table
    op.drop_index(op.f("ix_schools_id"), table_name="schools")
    op.drop_table("schools")
