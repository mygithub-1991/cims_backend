"""add expenses table

Revision ID: 20260401_000006
Revises: 20260401_000005
Create Date: 2026-04-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260401_000006'
down_revision = '20260401_000005'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'expenses',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('expense_date', sa.BigInteger(), nullable=False, index=True),
        sa.Column('payment_method', sa.String(50), nullable=False),
        sa.Column('vendor_name', sa.String(255), nullable=True),
        sa.Column('receipt_number', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.Column('updated_at', sa.BigInteger(), nullable=False),
        sa.Column('device_id', sa.String(255), nullable=True),
        sa.Column('last_synced_at', sa.BigInteger(), nullable=True)
    )

    # Create index on expense_date for faster querying
    op.create_index('ix_expenses_expense_date', 'expenses', ['expense_date'])
    op.create_index('ix_expenses_category', 'expenses', ['category'])


def downgrade():
    op.drop_index('ix_expenses_category', table_name='expenses')
    op.drop_index('ix_expenses_expense_date', table_name='expenses')
    op.drop_table('expenses')
