from sqlalchemy import Column, Integer, String, Float, BigInteger, Boolean, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from app.utils.timezone import now_ist, IST
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    ACCOUNTANT = "accountant"
    RECEPTION = "reception"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.RECEPTION)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_ist)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now_ist, onupdate=now_ist)
    last_login_at = Column(DateTime(timezone=True), nullable=True)


class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    school_name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=False)
    pincode = Column(String(20), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_ist)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now_ist, onupdate=now_ist)

    # Mobile device tracking
    device_id = Column(String(255), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)

    students = relationship("Student", back_populates="school")


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    contact_number = Column(String(20), nullable=False)
    salary = Column(Float, nullable=False)
    date_of_joining = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_ist)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now_ist, onupdate=now_ist)

    # Mobile device tracking
    device_id = Column(String(255), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)

    batches = relationship("Batch", back_populates="teacher")


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    time = Column(String(100), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="NO ACTION"), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_ist)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now_ist, onupdate=now_ist)

    # Mobile device tracking
    device_id = Column(String(255), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)

    teacher = relationship("Teacher", back_populates="batches")
    students = relationship("Student", back_populates="batch")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    roll_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    contact_number = Column(String(20), nullable=False)
    total_fees = Column(Float, nullable=False)
    # REMOVED: paid_fees column - now calculated dynamically from fee_records
    batch_id = Column(Integer, ForeignKey("batches.id", ondelete="NO ACTION"), nullable=False)
    payment_mode = Column(String(50), nullable=False)
    installment_type = Column(String(50), nullable=True)
    referred_by = Column(String(255), nullable=True)
    board = Column(String(100), nullable=True)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="NO ACTION"), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_ist)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now_ist, onupdate=now_ist)

    # Mobile device tracking
    device_id = Column(String(255), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)

    batch = relationship("Batch", back_populates="students")
    school = relationship("School", back_populates="students")
    fee_records = relationship("FeeRecord", back_populates="student")
    attendance_records = relationship("Attendance", back_populates="student")

    @property
    def paid_fees(self) -> float:
        """
        Calculate paid fees dynamically from fee_records.
        This is the single source of truth for paid fees.
        """
        return sum(
            record.amount_paid
            for record in self.fee_records
            if not record.is_deleted
        )


class FeeRecord(Base):
    __tablename__ = "fee_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="NO ACTION"), nullable=False)
    amount_paid = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    receipt_id = Column(String(50), unique=True, nullable=False, index=True)
    remarks = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_ist)

    # Mobile device tracking
    device_id = Column(String(255), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)

    student = relationship("Student", back_populates="fee_records")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="NO ACTION"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    is_present = Column(Boolean, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_ist)

    # Mobile device tracking
    device_id = Column(String(255), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)

    student = relationship("Student", back_populates="attendance_records")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False)  # Rent, Utilities, Salary, etc.
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    expense_date = Column(DateTime(timezone=True), nullable=False, index=True)
    payment_method = Column(String(50), nullable=False)  # Cash, UPI, Card, etc.
    vendor_name = Column(String(255), nullable=True)
    receipt_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_ist)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now_ist, onupdate=now_ist)

    # Mobile device tracking
    device_id = Column(String(255), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)


class SyncLog(Base):
    """Track sync operations from mobile devices"""
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # teacher, student, batch, etc.
    entity_id = Column(Integer, nullable=False)
    operation = Column(String(20), nullable=False)  # create, update, delete
    synced_at = Column(DateTime(timezone=True), nullable=False, default=now_ist)
    status = Column(String(20), nullable=False)  # success, failed
    error_message = Column(Text, nullable=True)
