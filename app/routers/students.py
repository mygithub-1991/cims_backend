from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Student
from app.schemas import StudentCreate, StudentUpdate, StudentResponse
import time

router = APIRouter()


@router.get("/", response_model=List[StudentResponse])
def get_students(
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
    batch_id: int = None,
    db: Session = Depends(get_db)
):
    """Get all students"""
    query = db.query(Student)
    if not include_deleted:
        query = query.filter(Student.is_deleted == False)
    if batch_id:
        query = query.filter(Student.batch_id == batch_id)
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

    current_time = int(time.time() * 1000)
    db_student = Student(
        **student.model_dump(exclude={"device_id"}),
        device_id=student.device_id,
        created_at=current_time,
        updated_at=current_time,
        last_synced_at=current_time
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
    if not update_data.get("updated_at"):
        update_data["updated_at"] = int(time.time() * 1000)
    update_data["last_synced_at"] = int(time.time() * 1000)

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
        db_student.deleted_at = int(time.time() * 1000)
        db_student.updated_at = int(time.time() * 1000)
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
    db_student.updated_at = int(time.time() * 1000)
    db.commit()
    db.refresh(db_student)
    return db_student
