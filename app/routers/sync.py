from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import School, Teacher, Batch, Student, FeeRecord, Attendance, Expense, SyncLog
from app.schemas import (
    SyncRequest, SyncResponse, SyncData,
    SchoolCreate, TeacherCreate, BatchCreate, StudentCreate, FeeRecordCreate, AttendanceCreate, ExpenseCreate,
    BulkSchoolCreate, BulkTeacherCreate, BulkBatchCreate, BulkStudentCreate, BulkFeeRecordCreate, BulkAttendanceCreate, BulkExpenseCreate
)
import time

router = APIRouter()


@router.post("/pull", response_model=SyncResponse)
def pull_sync(sync_request: SyncRequest, db: Session = Depends(get_db)):
    """
    Pull data from server that has been updated since last sync
    Client sends their last sync timestamp, server returns all changes since then
    """
    last_sync = sync_request.last_sync_timestamp
    server_timestamp = int(time.time() * 1000)

    # Fetch all data updated after last sync
    schools = db.query(School).filter(School.updated_at > last_sync).all()
    teachers = db.query(Teacher).filter(Teacher.updated_at > last_sync).all()
    batches = db.query(Batch).filter(Batch.updated_at > last_sync).all()
    students = db.query(Student).filter(Student.updated_at > last_sync).all()
    fee_records = db.query(FeeRecord).filter(FeeRecord.created_at > last_sync).all()
    attendance = db.query(Attendance).filter(Attendance.created_at > last_sync).all()
    expenses = db.query(Expense).filter(Expense.updated_at > last_sync).all()

    sync_data = SyncData(
        schools=schools,
        teachers=teachers,
        batches=batches,
        students=students,
        fee_records=fee_records,
        attendance=attendance,
        expenses=expenses
    )

    return SyncResponse(
        success=True,
        message=f"Synced {len(schools)} schools, {len(teachers)} teachers, {len(batches)} batches, "
                f"{len(students)} students, {len(fee_records)} fee records, "
                f"{len(attendance)} attendance records, {len(expenses)} expenses",
        server_timestamp=server_timestamp,
        data=sync_data
    )


@router.post("/push/schools")
def push_schools(bulk_data: BulkSchoolCreate, db: Session = Depends(get_db)):
    """Push school data from mobile device to server"""
    current_time = int(time.time() * 1000)
    created = 0
    updated = 0
    errors = []

    for school_data in bulk_data.schools:
        try:
            # Check if school exists by device_id or by matching unique fields
            existing = None
            if school_data.device_id:
                existing = db.query(School).filter(
                    School.device_id == school_data.device_id,
                    School.school_name == school_data.school_name
                ).first()

            if existing:
                # Update existing
                update_data = school_data.model_dump(exclude={"device_id"})
                update_data["updated_at"] = current_time
                update_data["last_synced_at"] = current_time

                for field, value in update_data.items():
                    setattr(existing, field, value)
                updated += 1
            else:
                # Create new
                db_school = School(
                    **school_data.model_dump(exclude={"device_id"}),
                    device_id=school_data.device_id,
                    created_at=current_time,
                    updated_at=current_time,
                    last_synced_at=current_time
                )
                db.add(db_school)
                created += 1

        except Exception as e:
            errors.append({"school": school_data.school_name, "error": str(e)})

    db.commit()

    return {
        "success": True,
        "created": created,
        "updated": updated,
        "errors": errors
    }


@router.post("/push/teachers")
def push_teachers(bulk_data: BulkTeacherCreate, db: Session = Depends(get_db)):
    """Push teacher data from mobile device to server"""
    current_time = int(time.time() * 1000)
    created = 0
    updated = 0
    errors = []

    for teacher_data in bulk_data.teachers:
        try:
            # Check if teacher exists by device_id or by matching unique fields
            existing = None
            if teacher_data.device_id:
                existing = db.query(Teacher).filter(
                    Teacher.device_id == teacher_data.device_id,
                    Teacher.name == teacher_data.name
                ).first()

            if existing:
                # Update existing
                update_data = teacher_data.model_dump(exclude={"device_id"})
                update_data["updated_at"] = current_time
                update_data["last_synced_at"] = current_time

                for field, value in update_data.items():
                    setattr(existing, field, value)
                updated += 1
            else:
                # Create new
                db_teacher = Teacher(
                    **teacher_data.model_dump(exclude={"device_id"}),
                    device_id=teacher_data.device_id,
                    created_at=current_time,
                    updated_at=current_time,
                    last_synced_at=current_time
                )
                db.add(db_teacher)
                created += 1

        except Exception as e:
            errors.append({"teacher": teacher_data.name, "error": str(e)})

    db.commit()

    return {
        "success": True,
        "created": created,
        "updated": updated,
        "errors": errors
    }


@router.post("/push/batches")
def push_batches(bulk_data: BulkBatchCreate, db: Session = Depends(get_db)):
    """Push batch data from mobile device to server"""
    current_time = int(time.time() * 1000)
    created = 0
    updated = 0
    errors = []

    for batch_data in bulk_data.batches:
        try:
            existing = None
            if batch_data.device_id:
                existing = db.query(Batch).filter(
                    Batch.device_id == batch_data.device_id,
                    Batch.name == batch_data.name
                ).first()

            if existing:
                update_data = batch_data.model_dump(exclude={"device_id"})
                update_data["updated_at"] = current_time
                update_data["last_synced_at"] = current_time

                for field, value in update_data.items():
                    setattr(existing, field, value)
                updated += 1
            else:
                db_batch = Batch(
                    **batch_data.model_dump(exclude={"device_id"}),
                    device_id=batch_data.device_id,
                    created_at=current_time,
                    updated_at=current_time,
                    last_synced_at=current_time
                )
                db.add(db_batch)
                created += 1

        except Exception as e:
            errors.append({"batch": batch_data.name, "error": str(e)})

    db.commit()

    return {
        "success": True,
        "created": created,
        "updated": updated,
        "errors": errors
    }


@router.post("/push/students")
def push_students(bulk_data: BulkStudentCreate, db: Session = Depends(get_db)):
    """Push student data from mobile device to server"""
    current_time = int(time.time() * 1000)
    created = 0
    updated = 0
    errors = []

    for student_data in bulk_data.students:
        try:
            # Check by roll number (unique identifier)
            existing = db.query(Student).filter(Student.roll_number == student_data.roll_number).first()

            if existing:
                update_data = student_data.model_dump(exclude={"device_id", "roll_number"})
                update_data["updated_at"] = current_time
                update_data["last_synced_at"] = current_time

                for field, value in update_data.items():
                    setattr(existing, field, value)
                updated += 1
            else:
                db_student = Student(
                    **student_data.model_dump(exclude={"device_id"}),
                    device_id=student_data.device_id,
                    created_at=current_time,
                    updated_at=current_time,
                    last_synced_at=current_time
                )
                db.add(db_student)
                created += 1

        except Exception as e:
            errors.append({"student": student_data.roll_number, "error": str(e)})

    db.commit()

    return {
        "success": True,
        "created": created,
        "updated": updated,
        "errors": errors
    }


@router.post("/push/fee-records")
def push_fee_records(bulk_data: BulkFeeRecordCreate, db: Session = Depends(get_db)):
    """Push fee record data from mobile device to server"""
    current_time = int(time.time() * 1000)
    created = 0
    skipped = 0
    errors = []

    for fee_data in bulk_data.fee_records:
        try:
            # Check by receipt ID (unique identifier)
            existing = db.query(FeeRecord).filter(FeeRecord.receipt_id == fee_data.receipt_id).first()

            if existing:
                skipped += 1
            else:
                db_fee = FeeRecord(
                    **fee_data.model_dump(exclude={"device_id"}),
                    device_id=fee_data.device_id,
                    created_at=current_time,
                    last_synced_at=current_time
                )
                db.add(db_fee)
                created += 1

        except Exception as e:
            errors.append({"receipt_id": fee_data.receipt_id, "error": str(e)})

    db.commit()

    return {
        "success": True,
        "created": created,
        "skipped": skipped,
        "errors": errors
    }


@router.post("/push/attendance")
def push_attendance(bulk_data: BulkAttendanceCreate, db: Session = Depends(get_db)):
    """Push attendance data from mobile device to server"""
    current_time = int(time.time() * 1000)
    created = 0
    errors = []

    for attendance_data in bulk_data.attendance:
        try:
            # Check for duplicate (same student, same date)
            existing = db.query(Attendance).filter(
                Attendance.student_id == attendance_data.student_id,
                Attendance.date == attendance_data.date
            ).first()

            if not existing:
                db_attendance = Attendance(
                    **attendance_data.model_dump(exclude={"device_id"}),
                    device_id=attendance_data.device_id,
                    created_at=current_time,
                    last_synced_at=current_time
                )
                db.add(db_attendance)
                created += 1

        except Exception as e:
            errors.append({"student_id": attendance_data.student_id, "error": str(e)})

    db.commit()

    return {
        "success": True,
        "created": created,
        "errors": errors
    }


@router.post("/push/expenses")
def push_expenses(bulk_data: BulkExpenseCreate, db: Session = Depends(get_db)):
    """Push expense data from mobile device to server"""
    current_time = int(time.time() * 1000)
    created = 0
    updated = 0
    errors = []

    for expense_data in bulk_data.expenses:
        try:
            # Check if expense with matching device_id and created_at exists
            existing = db.query(Expense).filter(
                Expense.device_id == expense_data.device_id,
                Expense.created_at == current_time
            ).first() if expense_data.device_id else None

            if existing:
                # Update existing
                for key, value in expense_data.model_dump(exclude_unset=True, exclude={"device_id"}).items():
                    setattr(existing, key, value)
                existing.last_synced_at = current_time
                existing.updated_at = current_time
                updated += 1
            else:
                # Create new
                db_expense = Expense(
                    **expense_data.model_dump(exclude={"device_id"}),
                    device_id=expense_data.device_id,
                    created_at=current_time,
                    updated_at=current_time,
                    last_synced_at=current_time
                )
                db.add(db_expense)
                created += 1

        except Exception as e:
            errors.append({"description": getattr(expense_data, 'description', 'Unknown'), "error": str(e)})

    db.commit()

    return {
        "success": True,
        "created": created,
        "updated": updated,
        "errors": errors
    }


@router.get("/status")
def sync_status(device_id: str, db: Session = Depends(get_db)):
    """Get sync status for a device"""
    last_sync = db.query(SyncLog).filter(
        SyncLog.device_id == device_id,
        SyncLog.status == "success"
    ).order_by(SyncLog.synced_at.desc()).first()

    if last_sync:
        return {
            "device_id": device_id,
            "last_sync_time": last_sync.synced_at,
            "last_sync_entity": last_sync.entity_type
        }
    else:
        return {
            "device_id": device_id,
            "last_sync_time": None,
            "message": "No sync history found"
        }
