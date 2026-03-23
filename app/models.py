from sqlalchemy import Column, Integer, String, Float, BigInteger, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    contact_number = Column(String(20), nullable=False)
    salary = Column(Float, nullable=False)
    date_of_joining = Column(BigInteger, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(BigInteger, nullable=True)
    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)

    # Mobile device tracking
    device_id = Column(String(255), nullable=True)
    last_synced_at = Column(BigInteger, nullable=True)

    batches = relationship("Batch", back_populates="teacher")


class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    time = Column(String(100), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="NO ACTION"), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(BigInteger, nullable=True)
    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)

    # Mobile device tracking
    device_id = Column(String(255), nullable=True)
    last_synced_at = Column(BigInteger, nullable=True)

    teacher = relationship("Teacher", back_populates="batches")
    students = relationship("Student", back_populates="batch")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    roll_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    contact_number = Column(String(20), nullable=False)
    total_fees = Column(Float, nullable=False)
    paid_fees = Column(Float, default=0.0, nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id", ondelete="NO ACTION"), nullable=False)
    payment_mode = Column(String(50), nullable=False)
    installment_type = Column(String(50), nullable=True)
    referred_by = Column(String(255), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(BigInteger, nullable=True)
    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)

    # Mobile device tracking
    device_id = Column(String(255), nullable=True)
    last_synced_at = Column(BigInteger, nullable=True)

    batch = relationship("Batch", back_populates="students")
    fee_records = relationship("FeeRecord", back_populates="student")
    attendance_records = relationship("Attendance", back_populates="student")


class FeeRecord(Base):
    __tablename__ = "fee_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="NO ACTION"), nullable=False)
    amount_paid = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    date = Column(BigInteger, nullable=False)
    receipt_id = Column(String(50), unique=True, nullable=False, index=True)
    remarks = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(BigInteger, nullable=True)
    created_at = Column(BigInteger, nullable=False)

    # Mobile device tracking
    device_id = Column(String(255), nullable=True)
    last_synced_at = Column(BigInteger, nullable=True)

    student = relationship("Student", back_populates="fee_records")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="NO ACTION"), nullable=False)
    date = Column(BigInteger, nullable=False, index=True)
    is_present = Column(Boolean, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(BigInteger, nullable=True)
    created_at = Column(BigInteger, nullable=False)

    # Mobile device tracking
    device_id = Column(String(255), nullable=True)
    last_synced_at = Column(BigInteger, nullable=True)

    student = relationship("Student", back_populates="attendance_records")


class SyncLog(Base):
    """Track sync operations from mobile devices"""
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # teacher, student, batch, etc.
    entity_id = Column(Integer, nullable=False)
    operation = Column(String(20), nullable=False)  # create, update, delete
    synced_at = Column(BigInteger, nullable=False)
    status = Column(String(20), nullable=False)  # success, failed
    error_message = Column(Text, nullable=True)
