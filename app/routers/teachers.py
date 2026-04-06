from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import Teacher
from app.schemas import TeacherCreate, TeacherUpdate, TeacherResponse, timestamp_to_datetime
from app.utils.timezone import now_ist

router = APIRouter()


@router.get("/", response_model=List[TeacherResponse])
def get_teachers(
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
    search: str = None,
    db: Session = Depends(get_db)
):
    """Get all teachers with optional search"""
    query = db.query(Teacher)
    if not include_deleted:
        query = query.filter(Teacher.is_deleted == False)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Teacher.name.ilike(search_pattern)) |
            (Teacher.subject.ilike(search_pattern)) |
            (Teacher.contact_number.ilike(search_pattern))
        )
    teachers = query.offset(skip).limit(limit).all()
    return teachers


@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """Get a specific teacher by ID"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


@router.post("/", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    """Create a new teacher"""
    # Convert timestamp to datetime for date_of_joining
    teacher_data = teacher.model_dump(exclude={"device_id"})
    teacher_data["date_of_joining"] = timestamp_to_datetime(teacher.date_of_joining)

    db_teacher = Teacher(
        **teacher_data,
        device_id=teacher.device_id,
        last_synced_at=now_ist()
        # created_at and updated_at use defaults from model
    )
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@router.put("/{teacher_id}", response_model=TeacherResponse)
def update_teacher(
    teacher_id: int,
    teacher: TeacherUpdate,
    db: Session = Depends(get_db)
):
    """Update a teacher"""
    db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    update_data = teacher.model_dump(exclude_unset=True)

    # Convert timestamp fields to datetime
    if "date_of_joining" in update_data and update_data["date_of_joining"] is not None:
        update_data["date_of_joining"] = timestamp_to_datetime(update_data["date_of_joining"])
    if "deleted_at" in update_data and update_data["deleted_at"] is not None:
        update_data["deleted_at"] = timestamp_to_datetime(update_data["deleted_at"])
    if "updated_at" in update_data and update_data["updated_at"] is not None:
        update_data["updated_at"] = timestamp_to_datetime(update_data["updated_at"])
    else:
        update_data["updated_at"] = now_ist()

    update_data["last_synced_at"] = now_ist()

    for field, value in update_data.items():
        setattr(db_teacher, field, value)

    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@router.delete("/{teacher_id}")
def delete_teacher(teacher_id: int, soft: bool = True, db: Session = Depends(get_db)):
    """Delete a teacher (soft delete by default)"""
    db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if soft:
        db_teacher.is_deleted = True
        db_teacher.deleted_at = now_ist()
        db_teacher.updated_at = now_ist()
        db.commit()
        return {"message": "Teacher soft deleted successfully"}
    else:
        db.delete(db_teacher)
        db.commit()
        return {"message": "Teacher permanently deleted"}


@router.post("/{teacher_id}/restore")
def restore_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """Restore a soft-deleted teacher"""
    db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    db_teacher.is_deleted = False
    db_teacher.deleted_at = None
    db_teacher.updated_at = now_ist()
    db.commit()
    db.refresh(db_teacher)
    return db_teacher
