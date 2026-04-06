from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import Student
from app.schemas import StudentCreate, StudentUpdate, StudentResponse, timestamp_to_datetime
from app.utils.timezone import now_ist

router = APIRouter()


@router.get("/", response_model=List[StudentResponse])
def get_students(
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
    batch_id: int = None,
    search: str = None,
    db: Session = Depends(get_db)
):
    """Get all students with optional search"""
    query = db.query(Student)
    if not include_deleted:
        query = query.filter(Student.is_deleted == False)
    if batch_id:
        query = query.filter(Student.batch_id == batch_id)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Student.name.ilike(search_pattern)) |
            (Student.roll_number.ilike(search_pattern)) |
            (Student.contact_number.ilike(search_pattern))
        )
    students = query.offset(skip).limit(limit).all()
    return students


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """Get a specific student by ID"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.get("/roll/{roll_number}", response_model=StudentResponse)
def get_student_by_roll(roll_number: str, db: Session = Depends(get_db)):
    """Get a student by roll number"""
    student = db.query(Student).filter(Student.roll_number == roll_number).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Create a new student"""
    # Check if roll number already exists
    existing = db.query(Student).filter(Student.roll_number == student.roll_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Roll number already exists")

    db_student = Student(
        **student.model_dump(exclude={"device_id"}),
        device_id=student.device_id,
        last_synced_at=now_ist()
        # created_at and updated_at use defaults from model
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student: StudentUpdate,
    db: Session = Depends(get_db)
):
    """Update a student"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    update_data = student.model_dump(exclude_unset=True)

    # Convert timestamp fields to datetime
    if "deleted_at" in update_data and update_data["deleted_at"] is not None:
        update_data["deleted_at"] = timestamp_to_datetime(update_data["deleted_at"])
    if "updated_at" in update_data and update_data["updated_at"] is not None:
        update_data["updated_at"] = timestamp_to_datetime(update_data["updated_at"])
    else:
        update_data["updated_at"] = now_ist()

    update_data["last_synced_at"] = now_ist()

    for field, value in update_data.items():
        setattr(db_student, field, value)

    db.commit()
    db.refresh(db_student)
    return db_student


@router.delete("/{student_id}")
def delete_student(student_id: int, soft: bool = True, db: Session = Depends(get_db)):
    """Delete a student (soft delete by default)"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    if soft:
        db_student.is_deleted = True
        db_student.deleted_at = now_ist()
        db_student.updated_at = now_ist()
        db.commit()
        return {"message": "Student soft deleted successfully"}
    else:
        db.delete(db_student)
        db.commit()
        return {"message": "Student permanently deleted"}


@router.post("/{student_id}/restore")
def restore_student(student_id: int, db: Session = Depends(get_db)):
    """Restore a soft-deleted student"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    db_student.is_deleted = False
    db_student.deleted_at = None
    db_student.updated_at = now_ist()
    db.commit()
    db.refresh(db_student)
    return db_student
