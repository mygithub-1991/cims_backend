"""Convert BigInteger datetime columns to DateTime with timezone

Revision ID: 20260406_000007
Revises: 20260401_000006
Create Date: 2026-04-06 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260406_000007'
down_revision = '20260401_000006'
branch_labels = None
depends_on = None


def upgrade():
    """
    Convert all BigInteger timestamp columns to TIMESTAMP WITH TIME ZONE.
    PostgreSQL stores timestamps in milliseconds, so we divide by 1000 and use to_timestamp().
    """

    # Users table
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN deleted_at TYPE TIMESTAMP WITH TIME ZONE
        USING CASE WHEN deleted_at IS NOT NULL THEN to_timestamp(deleted_at / 1000.0) ELSE NULL END,
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(created_at / 1000.0),
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(updated_at / 1000.0),
        ALTER COLUMN last_login_at TYPE TIMESTAMP WITH TIME ZONE
        USING CASE WHEN last_login_at IS NOT NULL THEN to_timestamp(last_login_at / 1000.0) ELSE NULL END
    """)

    # Schools table
    op.execute("""
        ALTER TABLE schools
        ALTER COLUMN deleted_at TYPE TIMESTAMP WITH TIME ZONE
        USING CASE WHEN deleted_at IS NOT NULL THEN to_timestamp(deleted_at / 1000.0) ELSE NULL END,
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(created_at / 1000.0),
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(updated_at / 1000.0),
        ALTER COLUMN last_synced_at TYPE TIMESTAMP WITH TIME ZONE
        USING CASE WHEN last_synced_at IS NOT NULL THEN to_timestamp(last_synced_at / 1000.0) ELSE NULL END
    """)

    # Teachers table
    op.execute("""
        ALTER TABLE teachers
        ALTER COLUMN date_of_joining TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(date_of_joining / 1000.0),
        ALTER COLUMN deleted_at TYPE TIMESTAMP WITH TIME ZONE
        USING CASE WHEN deleted_at IS NOT NULL THEN to_timestamp(deleted_at / 1000.0) ELSE NULL END,
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(created_at / 1000.0),
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(updated_at / 1000.0),
        ALTER COLUMN last_synced_at TYPE TIMESTAMP WITH TIME ZONE
        USING CASE WHEN last_synced_at IS NOT NULL THEN to_timestamp(last_synced_at / 1000.0) ELSE NULL END
    """)

    # Batches table
    op.execute("""
        ALTER TABLE batches
        ALTER COLUMN deleted_at TYPE TIMESTAMP WITH TIME ZONE
        USING CASE WHEN deleted_at IS NOT NULL THEN to_timestamp(deleted_at / 1000.0) ELSE NULL END,
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(created_at / 1000.0),
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(updated_at / 1000.0),
        ALTER COLUMN last_synced_at TYPE TIMESTAMP WITH TIME ZONE
        USING CASE WHEN last_synced_at IS NOT NULL THEN to_timestamp(last_synced_at / 1000.0) ELSE NULL END
    """)

    # Students table
    op.execute("""
        ALTER TABLE students
        ALTER COLUMN deleted_at TYPE TIMESTAMP WITH TIME ZONE
        USING CASE WHEN deleted_at IS NOT NULL THEN to_timestamp(deleted_at / 1000.0) ELSE NULL END,
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(created_at / 1000.0),
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(updated_at / 1000.0),
        ALTER COLUMN last_synced_at TYPE TIMESTAMP WITH TIME ZONE
        USING CASE WHEN last_synced_at IS NOT NULL THEN to_timestamp(last_synced_at / 1000.0) ELSE NULL END
    """)

    # Fee records table
    op.execute("""
        ALTER TABLE fee_records
        ALTER COLUMN date TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(date / 1000.0),
        ALTER COLUMN deleted_at TYPE TIMESTAMP WITH TIME ZONE
        USING CASE WHEN deleted_at IS NOT NULL THEN to_timestamp(deleted_at / 1000.0) ELSE NULL END,
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(created_at / 1000.0),
        ALTER COLUMN last_synced_at TYPE TIMESTAMP WITH TIME ZONE
        USING CASE WHEN last_synced_at IS NOT NULL THEN to_timestamp(last_synced_at / 1000.0) ELSE NULL END
    """)

    # Attendance table
    op.execute("""
        ALTER TABLE attendance
        ALTER COLUMN date TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(date / 1000.0),
        ALTER COLUMN deleted_at TYPE TIMESTAMP WITH TIME ZONE
        USING CASE WHEN deleted_at IS NOT NULL THEN to_timestamp(deleted_at / 1000.0) ELSE NULL END,
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(created_at / 1000.0),
        ALTER COLUMN last_synced_at TYPE TIMESTAMP WITH TIME ZONE
        USING CASE WHEN last_synced_at IS NOT NULL THEN to_timestamp(last_synced_at / 1000.0) ELSE NULL END
    """)

    # Expenses table
    op.execute("""
        ALTER TABLE expenses
        ALTER COLUMN expense_date TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(expense_date / 1000.0),
        ALTER COLUMN deleted_at TYPE TIMESTAMP WITH TIME ZONE
        USING CASE WHEN deleted_at IS NOT NULL THEN to_timestamp(deleted_at / 1000.0) ELSE NULL END,
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(created_at / 1000.0),
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(updated_at / 1000.0),
        ALTER COLUMN last_synced_at TYPE TIMESTAMP WITH TIME ZONE
        USING CASE WHEN last_synced_at IS NOT NULL THEN to_timestamp(last_synced_at / 1000.0) ELSE NULL END
    """)

    # Sync logs table
    op.execute("""
        ALTER TABLE sync_logs
        ALTER COLUMN synced_at TYPE TIMESTAMP WITH TIME ZONE
        USING to_timestamp(synced_at / 1000.0)
    """)


def downgrade():
    """
    Convert back to BigInteger (milliseconds since epoch).
    """

    # Users table
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN deleted_at TYPE BIGINT
        USING CASE WHEN deleted_at IS NOT NULL THEN EXTRACT(EPOCH FROM deleted_at)::BIGINT * 1000 ELSE NULL END,
        ALTER COLUMN created_at TYPE BIGINT
        USING EXTRACT(EPOCH FROM created_at)::BIGINT * 1000,
        ALTER COLUMN updated_at TYPE BIGINT
        USING EXTRACT(EPOCH FROM updated_at)::BIGINT * 1000,
        ALTER COLUMN last_login_at TYPE BIGINT
        USING CASE WHEN last_login_at IS NOT NULL THEN EXTRACT(EPOCH FROM last_login_at)::BIGINT * 1000 ELSE NULL END
    """)

    # Schools table
    op.execute("""
        ALTER TABLE schools
        ALTER COLUMN deleted_at TYPE BIGINT
        USING CASE WHEN deleted_at IS NOT NULL THEN EXTRACT(EPOCH FROM deleted_at)::BIGINT * 1000 ELSE NULL END,
        ALTER COLUMN created_at TYPE BIGINT
        USING EXTRACT(EPOCH FROM created_at)::BIGINT * 1000,
        ALTER COLUMN updated_at TYPE BIGINT
        USING EXTRACT(EPOCH FROM updated_at)::BIGINT * 1000,
        ALTER COLUMN last_synced_at TYPE BIGINT
        USING CASE WHEN last_synced_at IS NOT NULL THEN EXTRACT(EPOCH FROM last_synced_at)::BIGINT * 1000 ELSE NULL END
    """)

    # Teachers table
    op.execute("""
        ALTER TABLE teachers
        ALTER COLUMN date_of_joining TYPE BIGINT
        USING EXTRACT(EPOCH FROM date_of_joining)::BIGINT * 1000,
        ALTER COLUMN deleted_at TYPE BIGINT
        USING CASE WHEN deleted_at IS NOT NULL THEN EXTRACT(EPOCH FROM deleted_at)::BIGINT * 1000 ELSE NULL END,
        ALTER COLUMN created_at TYPE BIGINT
        USING EXTRACT(EPOCH FROM created_at)::BIGINT * 1000,
        ALTER COLUMN updated_at TYPE BIGINT
        USING EXTRACT(EPOCH FROM updated_at)::BIGINT * 1000,
        ALTER COLUMN last_synced_at TYPE BIGINT
        USING CASE WHEN last_synced_at IS NOT NULL THEN EXTRACT(EPOCH FROM last_synced_at)::BIGINT * 1000 ELSE NULL END
    """)

    # Batches table
    op.execute("""
        ALTER TABLE batches
        ALTER COLUMN deleted_at TYPE BIGINT
        USING CASE WHEN deleted_at IS NOT NULL THEN EXTRACT(EPOCH FROM deleted_at)::BIGINT * 1000 ELSE NULL END,
        ALTER COLUMN created_at TYPE BIGINT
        USING EXTRACT(EPOCH FROM created_at)::BIGINT * 1000,
        ALTER COLUMN updated_at TYPE BIGINT
        USING EXTRACT(EPOCH FROM updated_at)::BIGINT * 1000,
        ALTER COLUMN last_synced_at TYPE BIGINT
        USING CASE WHEN last_synced_at IS NOT NULL THEN EXTRACT(EPOCH FROM last_synced_at)::BIGINT * 1000 ELSE NULL END
    """)

    # Students table
    op.execute("""
        ALTER TABLE students
        ALTER COLUMN deleted_at TYPE BIGINT
        USING CASE WHEN deleted_at IS NOT NULL THEN EXTRACT(EPOCH FROM deleted_at)::BIGINT * 1000 ELSE NULL END,
        ALTER COLUMN created_at TYPE BIGINT
        USING EXTRACT(EPOCH FROM created_at)::BIGINT * 1000,
        ALTER COLUMN updated_at TYPE BIGINT
        USING EXTRACT(EPOCH FROM updated_at)::BIGINT * 1000,
        ALTER COLUMN last_synced_at TYPE BIGINT
        USING CASE WHEN last_synced_at IS NOT NULL THEN EXTRACT(EPOCH FROM last_synced_at)::BIGINT * 1000 ELSE NULL END
    """)

    # Fee records table
    op.execute("""
        ALTER TABLE fee_records
        ALTER COLUMN date TYPE BIGINT
        USING EXTRACT(EPOCH FROM date)::BIGINT * 1000,
        ALTER COLUMN deleted_at TYPE BIGINT
        USING CASE WHEN deleted_at IS NOT NULL THEN EXTRACT(EPOCH FROM deleted_at)::BIGINT * 1000 ELSE NULL END,
        ALTER COLUMN created_at TYPE BIGINT
        USING EXTRACT(EPOCH FROM created_at)::BIGINT * 1000,
        ALTER COLUMN last_synced_at TYPE BIGINT
        USING CASE WHEN last_synced_at IS NOT NULL THEN EXTRACT(EPOCH FROM last_synced_at)::BIGINT * 1000 ELSE NULL END
    """)

    # Attendance table
    op.execute("""
        ALTER TABLE attendance
        ALTER COLUMN date TYPE BIGINT
        USING EXTRACT(EPOCH FROM date)::BIGINT * 1000,
        ALTER COLUMN deleted_at TYPE BIGINT
        USING CASE WHEN deleted_at IS NOT NULL THEN EXTRACT(EPOCH FROM deleted_at)::BIGINT * 1000 ELSE NULL END,
        ALTER COLUMN created_at TYPE BIGINT
        USING EXTRACT(EPOCH FROM created_at)::BIGINT * 1000,
        ALTER COLUMN last_synced_at TYPE BIGINT
        USING CASE WHEN last_synced_at IS NOT NULL THEN EXTRACT(EPOCH FROM last_synced_at)::BIGINT * 1000 ELSE NULL END
    """)

    # Expenses table
    op.execute("""
        ALTER TABLE expenses
        ALTER COLUMN expense_date TYPE BIGINT
        USING EXTRACT(EPOCH FROM expense_date)::BIGINT * 1000,
        ALTER COLUMN deleted_at TYPE BIGINT
        USING CASE WHEN deleted_at IS NOT NULL THEN EXTRACT(EPOCH FROM deleted_at)::BIGINT * 1000 ELSE NULL END,
        ALTER COLUMN created_at TYPE BIGINT
        USING EXTRACT(EPOCH FROM created_at)::BIGINT * 1000,
        ALTER COLUMN updated_at TYPE BIGINT
        USING EXTRACT(EPOCH FROM updated_at)::BIGINT * 1000,
        ALTER COLUMN last_synced_at TYPE BIGINT
        USING CASE WHEN last_synced_at IS NOT NULL THEN EXTRACT(EPOCH FROM last_synced_at)::BIGINT * 1000 ELSE NULL END
    """)

    # Sync logs table
    op.execute("""
        ALTER TABLE sync_logs
        ALTER COLUMN synced_at TYPE BIGINT
        USING EXTRACT(EPOCH FROM synced_at)::BIGINT * 1000
    """)
