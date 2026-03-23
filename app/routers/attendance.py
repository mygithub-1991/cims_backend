from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Attendance
from app.schemas import AttendanceCreate, AttendanceResponse
import time

router = APIRouter()


@router.get("/", response_model=List[AttendanceResponse])
def get_attendance(
    skip: int = 0,
    limit: int = 100,
    student_id: int = None,
    date: int = None,
    db: Session = Depends(get_db)
):
    """Get attendance records"""
    query = db.query(Attendance).filter(Attendance.is_deleted == False)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    if date:
        query = query.filter(Attendance.date == date)
    attendance = query.offset(skip).limit(limit).all()
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
    current_time = int(time.time() * 1000)
    db_attendance = Attendance(
        **attendance.model_dump(exclude={"device_id"}),
        device_id=attendance.device_id,
        created_at=current_time,
        last_synced_at=current_time
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
    current_time = int(time.time() * 1000)
    db_attendance_list = []

    for attendance in attendance_list:
        db_attendance = Attendance(
            **attendance.model_dump(exclude={"device_id"}),
            device_id=attendance.device_id,
            created_at=current_time,
            last_synced_at=current_time
        )
        db_attendance_list.append(db_attendance)

    db.add_all(db_attendance_list)
    db.commit()

    for record in db_attendance_list:
        db.refresh(record)

    return db_attendance_list
