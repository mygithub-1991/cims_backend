"""Remove paid_fees column from students table

Revision ID: 20260408_000009
Revises: 20260407_000008
Create Date: 2026-04-08 00:00:00

Rationale:
The paid_fees column is denormalized data that causes inconsistencies when
fee records are deleted or voided. By removing this column and calculating
paid_fees dynamically from fee_records table, we ensure:
1. Single source of truth (fee_records table)
2. Automatic consistency - no manual synchronization needed
3. Correct calculations even after deletions/voids

The Student model now has a @property paid_fees that calculates the sum
from related fee_records where is_deleted=False.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260408_000009"
down_revision: Union[str, None] = "20260407_000008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove paid_fees column - now calculated from fee_records"""
    # Drop the paid_fees column from students table
    op.drop_column('students', 'paid_fees')


def downgrade() -> None:
    """Re-add paid_fees column if migration needs to be rolled back"""
    # Add back the paid_fees column with default value of 0.0
    op.add_column('students', sa.Column('paid_fees', sa.Float(), nullable=False, server_default='0.0'))

    # Note: Downgrade will add the column back but values will be 0.0
    # To restore actual values, would need to recalculate from fee_records:
    # UPDATE students SET paid_fees = (
    #     SELECT COALESCE(SUM(amount_paid), 0.0)
    #     FROM fee_records
    #     WHERE fee_records.student_id = students.id
    #     AND fee_records.is_deleted = false
    # );
