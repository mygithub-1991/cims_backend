"""Add school_id to students table

Revision ID: 20260401_000005
Revises: 20260401_000004
Create Date: 2026-04-01 00:15:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260401_000005"
down_revision: Union[str, None] = "20260401_000004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add school_id column to students table
    op.add_column('students', sa.Column('school_id', sa.Integer(), nullable=True))

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_students_school_id',
        'students', 'schools',
        ['school_id'], ['id'],
        ondelete='NO ACTION'
    )


def downgrade() -> None:
    # Remove foreign key constraint
    op.drop_constraint('fk_students_school_id', 'students', type_='foreignkey')

    # Remove school_id column
    op.drop_column('students', 'school_id')
