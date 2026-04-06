from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import Attendance, Student
from app.schemas import AttendanceCreate, AttendanceResponse, timestamp_to_datetime
from app.utils.timezone import now_ist

router = APIRouter()


@router.get("/", response_model=List[AttendanceResponse])
def get_attendance(
    skip: int = 0,
    limit: int = 100,
    student_id: Optional[int] = None,
    date: Optional[int] = None,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get attendance records with enhanced filtering"""
    query = db.query(Attendance).filter(Attendance.is_deleted == False)

    if student_id:
        query = query.filter(Attendance.student_id == student_id)

    # Convert timestamp parameters to datetime for comparison
    if date:
        date_dt = timestamp_to_datetime(date)
        query = query.filter(func.date(Attendance.date) == func.date(date_dt))
    elif start_date and end_date:
        start_dt = timestamp_to_datetime(start_date)
        end_dt = timestamp_to_datetime(end_date)
        query = query.filter(and_(
            Attendance.date >= start_dt,
            Attendance.date <= end_dt
        ))
    elif start_date:
        start_dt = timestamp_to_datetime(start_date)
        query = query.filter(Attendance.date >= start_dt)
    elif end_date:
        end_dt = timestamp_to_datetime(end_date)
        query = query.filter(Attendance.date <= end_dt)

    attendance = query.order_by(Attendance.date.desc()).offset(skip).limit(limit).all()
    return attendance


@router.get("/{attendance_id}", response_model=AttendanceResponse)
def get_attendance_record(attendance_id: int, db: Session = Depends(get_db)):
    """Get a specific attendance record by ID"""
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return attendance


@router.post("/", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    """Create a new attendance record"""
    # Convert timestamp to datetime for date field
    attendance_data = attendance.model_dump(exclude={"device_id"})
    attendance_data["date"] = timestamp_to_datetime(attendance.date)

    db_attendance = Attendance(
        **attendance_data,
        device_id=attendance.device_id,
        last_synced_at=now_ist()
        # created_at uses default from model
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance


@router.post("/bulk", response_model=List[AttendanceResponse], status_code=status.HTTP_201_CREATED)
def create_bulk_attendance(
    attendance_list: List[AttendanceCreate],
    db: Session = Depends(get_db)
):
    """Create multiple attendance records at once"""
    db_attendance_list = []

    for attendance in attendance_list:
        # Convert timestamp to datetime for date field
        attendance_data = attendance.model_dump(exclude={"device_id"})
        attendance_data["date"] = timestamp_to_datetime(attendance.date)

        db_attendance = Attendance(
            **attendance_data,
            device_id=attendance.device_id,
            last_synced_at=now_ist()
            # created_at uses default from model
        )
        db_attendance_list.append(db_attendance)

    db.add_all(db_attendance_list)
    db.commit()

    for record in db_attendance_list:
        db.refresh(record)

    return db_attendance_list


@router.get("/by-batch/{batch_id}", response_model=List[AttendanceResponse])
def get_attendance_by_batch(
    batch_id: int,
    date: Optional[int] = None,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get attendance records for a specific batch"""
    # Get students in the batch
    students = db.query(Student).filter(
        Student.batch_id == batch_id,
        Student.is_deleted == False
    ).all()

    if not students:
        return []

    student_ids = [s.id for s in students]

    query = db.query(Attendance).filter(
        Attendance.student_id.in_(student_ids),
        Attendance.is_deleted == False
    )

    # Convert timestamp parameters to datetime for comparison
    if date:
        date_dt = timestamp_to_datetime(date)
        query = query.filter(func.date(Attendance.date) == func.date(date_dt))
    elif start_date and end_date:
        start_dt = timestamp_to_datetime(start_date)
        end_dt = timestamp_to_datetime(end_date)
        query = query.filter(and_(
            Attendance.date >= start_dt,
            Attendance.date <= end_dt
        ))

    return query.order_by(Attendance.date.desc()).all()


@router.get("/stats/summary")
def get_attendance_summary(
    student_id: Optional[int] = None,
    batch_id: Optional[int] = None,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get attendance statistics"""
    query = db.query(Attendance).filter(Attendance.is_deleted == False)

    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    elif batch_id:
        # Get students in batch
        students = db.query(Student).filter(
            Student.batch_id == batch_id,
            Student.is_deleted == False
        ).all()
        student_ids = [s.id for s in students]
        query = query.filter(Attendance.student_id.in_(student_ids))

    if start_date:
        query = query.filter(Attendance.date >= start_date)

    if end_date:
        query = query.filter(Attendance.date <= end_date)

    records = query.all()

    total = len(records)
    present = sum(1 for r in records if r.is_present)
    absent = total - present
    percentage = (present / total * 100) if total > 0 else 0.0

    return {
        "total_records": total,
        "present": present,
        "absent": absent,
        "attendance_percentage": round(percentage, 2)
    }
