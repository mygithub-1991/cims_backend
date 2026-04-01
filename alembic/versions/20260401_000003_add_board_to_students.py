"""Add board column to students table

Revision ID: 20260401_000003
Revises: 20260323_000002
Create Date: 2026-04-01 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260401_000003"
down_revision: Union[str, None] = "20260323_000002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add board column to students table
    op.add_column('students', sa.Column('board', sa.String(length=100), nullable=True))


def downgrade() -> None:
    # Remove board column from students table
    op.drop_column('students', 'board')
