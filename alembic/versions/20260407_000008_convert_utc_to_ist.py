"""Convert existing UTC timestamps to IST

Revision ID: 20260407_000008
Revises: 20260406_000007
Create Date: 2026-04-07 00:00:00.000000

This migration adds 5 hours 30 minutes to all existing timestamps.
After this migration, timestamps will represent IST time (but still stored with timezone info).
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260407_000008'
down_revision = '20260406_000007'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add 5 hours 30 minutes to all existing timestamps to convert UTC to IST.

    Note: PostgreSQL stores TIMESTAMP WITH TIME ZONE in UTC internally.
    This migration adds the offset so the actual instant is preserved but
    represents IST local time.
    """

    # Users table
    op.execute("""
        UPDATE users
        SET
            created_at = created_at + INTERVAL '5 hours 30 minutes',
            updated_at = updated_at + INTERVAL '5 hours 30 minutes',
            deleted_at = CASE
                WHEN deleted_at IS NOT NULL
                THEN deleted_at + INTERVAL '5 hours 30 minutes'
                ELSE NULL
            END,
            last_login_at = CASE
                WHEN last_login_at IS NOT NULL
                THEN last_login_at + INTERVAL '5 hours 30 minutes'
                ELSE NULL
            END
        WHERE id IS NOT NULL
    """)

    # Schools table
    op.execute("""
        UPDATE schools
        SET
            created_at = created_at + INTERVAL '5 hours 30 minutes',
            updated_at = updated_at + INTERVAL '5 hours 30 minutes',
            deleted_at = CASE
                WHEN deleted_at IS NOT NULL
                THEN deleted_at + INTERVAL '5 hours 30 minutes'
                ELSE NULL
            END,
            last_synced_at = CASE
                WHEN last_synced_at IS NOT NULL
                THEN last_synced_at + INTERVAL '5 hours 30 minutes'
                ELSE NULL
            END
        WHERE id IS NOT NULL
    """)

    # Teachers table
    op.execute("""
        UPDATE teachers
        SET
            date_of_joining = date_of_joining + INTERVAL '5 hours 30 minutes',
            created_at = created_at + INTERVAL '5 hours 30 minutes',
            updated_at = updated_at + INTERVAL '5 hours 30 minutes',
            deleted_at = CASE
                WHEN deleted_at IS NOT NULL
                THEN deleted_at + INTERVAL '5 hours 30 minutes'
                ELSE NULL
            END,
            last_synced_at = CASE
                WHEN last_synced_at IS NOT NULL
                THEN last_synced_at + INTERVAL '5 hours 30 minutes'
                ELSE NULL
            END
        WHERE id IS NOT NULL
    """)

    # Batches table
    op.execute("""
        UPDATE batches
        SET
            created_at = created_at + INTERVAL '5 hours 30 minutes',
            updated_at = updated_at + INTERVAL '5 hours 30 minutes',
            deleted_at = CASE
                WHEN deleted_at IS NOT NULL
                THEN deleted_at + INTERVAL '5 hours 30 minutes'
                ELSE NULL
            END,
            last_synced_at = CASE
                WHEN last_synced_at IS NOT NULL
                THEN last_synced_at + INTERVAL '5 hours 30 minutes'
                ELSE NULL
            END
        WHERE id IS NOT NULL
    """)

    # Students table
    op.execute("""
        UPDATE students
        SET
            created_at = created_at + INTERVAL '5 hours 30 minutes',
            updated_at = updated_at + INTERVAL '5 hours 30 minutes',
            deleted_at = CASE
                WHEN deleted_at IS NOT NULL
                THEN deleted_at + INTERVAL '5 hours 30 minutes'
                ELSE NULL
            END,
            last_synced_at = CASE
                WHEN last_synced_at IS NOT NULL
                THEN last_synced_at + INTERVAL '5 hours 30 minutes'
                ELSE NULL
            END
        WHERE id IS NOT NULL
    """)

    # Fee records table
    op.execute("""
        UPDATE fee_records
        SET
            date = date + INTERVAL '5 hours 30 minutes',
            created_at = created_at + INTERVAL '5 hours 30 minutes',
            deleted_at = CASE
                WHEN deleted_at IS NOT NULL
                THEN deleted_at + INTERVAL '5 hours 30 minutes'
                ELSE NULL
            END,
            last_synced_at = CASE
                WHEN last_synced_at IS NOT NULL
                THEN last_synced_at + INTERVAL '5 hours 30 minutes'
                ELSE NULL
            END
        WHERE id IS NOT NULL
    """)

    # Attendance table
    op.execute("""
        UPDATE attendance
        SET
            date = date + INTERVAL '5 hours 30 minutes',
            created_at = created_at + INTERVAL '5 hours 30 minutes',
            deleted_at = CASE
                WHEN deleted_at IS NOT NULL
                THEN deleted_at + INTERVAL '5 hours 30 minutes'
                ELSE NULL
            END,
            last_synced_at = CASE
                WHEN last_synced_at IS NOT NULL
                THEN last_synced_at + INTERVAL '5 hours 30 minutes'
                ELSE NULL
            END
        WHERE id IS NOT NULL
    """)

    # Expenses table
    op.execute("""
        UPDATE expenses
        SET
            expense_date = expense_date + INTERVAL '5 hours 30 minutes',
            created_at = created_at + INTERVAL '5 hours 30 minutes',
            updated_at = updated_at + INTERVAL '5 hours 30 minutes',
            deleted_at = CASE
                WHEN deleted_at IS NOT NULL
                THEN deleted_at + INTERVAL '5 hours 30 minutes'
                ELSE NULL
            END,
            last_synced_at = CASE
                WHEN last_synced_at IS NOT NULL
                THEN last_synced_at + INTERVAL '5 hours 30 minutes'
                ELSE NULL
            END
        WHERE id IS NOT NULL
    """)

    # Sync logs table
    op.execute("""
        UPDATE sync_logs
        SET
            synced_at = synced_at + INTERVAL '5 hours 30 minutes'
        WHERE id IS NOT NULL
    """)


def downgrade():
    """
    Convert IST timestamps back to UTC by subtracting 5 hours 30 minutes.
    """

    # Users table
    op.execute("""
        UPDATE users
        SET
            created_at = created_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            updated_at = updated_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            deleted_at = CASE
                WHEN deleted_at IS NOT NULL
                THEN deleted_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
                ELSE NULL
            END,
            last_login_at = CASE
                WHEN last_login_at IS NOT NULL
                THEN last_login_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
                ELSE NULL
            END
        WHERE id IS NOT NULL
    """)

    # Schools table
    op.execute("""
        UPDATE schools
        SET
            created_at = created_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            updated_at = updated_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            deleted_at = CASE
                WHEN deleted_at IS NOT NULL
                THEN deleted_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
                ELSE NULL
            END,
            last_synced_at = CASE
                WHEN last_synced_at IS NOT NULL
                THEN last_synced_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
                ELSE NULL
            END
        WHERE id IS NOT NULL
    """)

    # Teachers table
    op.execute("""
        UPDATE teachers
        SET
            date_of_joining = date_of_joining AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            created_at = created_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            updated_at = updated_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            deleted_at = CASE
                WHEN deleted_at IS NOT NULL
                THEN deleted_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
                ELSE NULL
            END,
            last_synced_at = CASE
                WHEN last_synced_at IS NOT NULL
                THEN last_synced_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
                ELSE NULL
            END
        WHERE id IS NOT NULL
    """)

    # Batches table
    op.execute("""
        UPDATE batches
        SET
            created_at = created_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            updated_at = updated_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            deleted_at = CASE
                WHEN deleted_at IS NOT NULL
                THEN deleted_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
                ELSE NULL
            END,
            last_synced_at = CASE
                WHEN last_synced_at IS NOT NULL
                THEN last_synced_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
                ELSE NULL
            END
        WHERE id IS NOT NULL
    """)

    # Students table
    op.execute("""
        UPDATE students
        SET
            created_at = created_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            updated_at = updated_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            deleted_at = CASE
                WHEN deleted_at IS NOT NULL
                THEN deleted_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
                ELSE NULL
            END,
            last_synced_at = CASE
                WHEN last_synced_at IS NOT NULL
                THEN last_synced_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
                ELSE NULL
            END
        WHERE id IS NOT NULL
    """)

    # Fee records table
    op.execute("""
        UPDATE fee_records
        SET
            date = date AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            created_at = created_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            deleted_at = CASE
                WHEN deleted_at IS NOT NULL
                THEN deleted_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
                ELSE NULL
            END,
            last_synced_at = CASE
                WHEN last_synced_at IS NOT NULL
                THEN last_synced_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
                ELSE NULL
            END
        WHERE id IS NOT NULL
    """)

    # Attendance table
    op.execute("""
        UPDATE attendance
        SET
            date = date AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            created_at = created_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            deleted_at = CASE
                WHEN deleted_at IS NOT NULL
                THEN deleted_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
                ELSE NULL
            END,
            last_synced_at = CASE
                WHEN last_synced_at IS NOT NULL
                THEN last_synced_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
                ELSE NULL
            END
        WHERE id IS NOT NULL
    """)

    # Expenses table
    op.execute("""
        UPDATE expenses
        SET
            expense_date = expense_date AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            created_at = created_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            updated_at = updated_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC',
            deleted_at = CASE
                WHEN deleted_at IS NOT NULL
                THEN deleted_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
                ELSE NULL
            END,
            last_synced_at = CASE
                WHEN last_synced_at IS NOT NULL
                THEN last_synced_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
                ELSE NULL
            END
        WHERE id IS NOT NULL
    """)

    # Sync logs table
    op.execute("""
        UPDATE sync_logs
        SET
            synced_at = synced_at AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC'
        WHERE id IS NOT NULL
    """)
