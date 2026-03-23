"""Initial schema

Revision ID: 20260323_000001
Revises:
Create Date: 2026-03-23 22:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260323_000001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "teachers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("contact_number", sa.String(length=20), nullable=False),
        sa.Column("salary", sa.Float(), nullable=False),
        sa.Column("date_of_joining", sa.BigInteger(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("device_id", sa.String(length=255), nullable=True),
        sa.Column("last_synced_at", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_teachers_id"), "teachers", ["id"], unique=False)

    op.create_table(
        "sync_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.String(length=255), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("operation", sa.String(length=20), nullable=False),
        sa.Column("synced_at", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sync_logs_device_id"), "sync_logs", ["device_id"], unique=False)
    op.create_index(op.f("ix_sync_logs_id"), "sync_logs", ["id"], unique=False)

    op.create_table(
        "batches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("time", sa.String(length=100), nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("device_id", sa.String(length=255), nullable=True),
        sa.Column("last_synced_at", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"], ondelete="NO ACTION"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_batches_id"), "batches", ["id"], unique=False)

    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("roll_number", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("contact_number", sa.String(length=20), nullable=False),
        sa.Column("total_fees", sa.Float(), nullable=False),
        sa.Column("paid_fees", sa.Float(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=False),
        sa.Column("payment_mode", sa.String(length=50), nullable=False),
        sa.Column("installment_type", sa.String(length=50), nullable=True),
        sa.Column("referred_by", sa.String(length=255), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.Column("device_id", sa.String(length=255), nullable=True),
        sa.Column("last_synced_at", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["batch_id"], ["batches.id"], ondelete="NO ACTION"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("roll_number"),
    )
    op.create_index(op.f("ix_students_id"), "students", ["id"], unique=False)
    op.create_index(op.f("ix_students_roll_number"), "students", ["roll_number"], unique=True)

    op.create_table(
        "attendance",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.BigInteger(), nullable=False),
        sa.Column("is_present", sa.Boolean(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("device_id", sa.String(length=255), nullable=True),
        sa.Column("last_synced_at", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="NO ACTION"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_attendance_date"), "attendance", ["date"], unique=False)
    op.create_index(op.f("ix_attendance_id"), "attendance", ["id"], unique=False)

    op.create_table(
        "fee_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("amount_paid", sa.Float(), nullable=False),
        sa.Column("payment_method", sa.String(length=50), nullable=False),
        sa.Column("date", sa.BigInteger(), nullable=False),
        sa.Column("receipt_id", sa.String(length=50), nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("device_id", sa.String(length=255), nullable=True),
        sa.Column("last_synced_at", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="NO ACTION"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("receipt_id"),
    )
    op.create_index(op.f("ix_fee_records_id"), "fee_records", ["id"], unique=False)
    op.create_index(op.f("ix_fee_records_receipt_id"), "fee_records", ["receipt_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_fee_records_receipt_id"), table_name="fee_records")
    op.drop_index(op.f("ix_fee_records_id"), table_name="fee_records")
    op.drop_table("fee_records")

    op.drop_index(op.f("ix_attendance_id"), table_name="attendance")
    op.drop_index(op.f("ix_attendance_date"), table_name="attendance")
    op.drop_table("attendance")

    op.drop_index(op.f("ix_students_roll_number"), table_name="students")
    op.drop_index(op.f("ix_students_id"), table_name="students")
    op.drop_table("students")

    op.drop_index(op.f("ix_batches_id"), table_name="batches")
    op.drop_table("batches")

    op.drop_index(op.f("ix_sync_logs_id"), table_name="sync_logs")
    op.drop_index(op.f("ix_sync_logs_device_id"), table_name="sync_logs")
    op.drop_table("sync_logs")

    op.drop_index(op.f("ix_teachers_id"), table_name="teachers")
    op.drop_table("teachers")