from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import School
from app.schemas import SchoolCreate, SchoolUpdate, SchoolResponse
import time

router = APIRouter()


@router.get("/", response_model=List[SchoolResponse])
def get_schools(
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
    db: Session = Depends(get_db)
):
    """Get all schools"""
    query = db.query(School)
    if not include_deleted:
        query = query.filter(School.is_deleted == False)
    schools = query.offset(skip).limit(limit).all()
    return schools


@router.get("/{school_id}", response_model=SchoolResponse)
def get_school(school_id: int, db: Session = Depends(get_db)):
    """Get a specific school by ID"""
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school


@router.post("/", response_model=SchoolResponse, status_code=status.HTTP_201_CREATED)
def create_school(school: SchoolCreate, db: Session = Depends(get_db)):
    """Create a new school"""
    current_time = int(time.time() * 1000)
    db_school = School(
        **school.model_dump(exclude={"device_id"}),
        device_id=school.device_id,
        created_at=current_time,
        updated_at=current_time,
        last_synced_at=current_time
    )
    db.add(db_school)
    db.commit()
    db.refresh(db_school)
    return db_school


@router.put("/{school_id}", response_model=SchoolResponse)
def update_school(
    school_id: int,
    school: SchoolUpdate,
    db: Session = Depends(get_db)
):
    """Update a school"""
    db_school = db.query(School).filter(School.id == school_id).first()
    if not db_school:
        raise HTTPException(status_code=404, detail="School not found")

    update_data = school.model_dump(exclude_unset=True)
    if not update_data.get("updated_at"):
        update_data["updated_at"] = int(time.time() * 1000)
    update_data["last_synced_at"] = int(time.time() * 1000)

    for field, value in update_data.items():
        setattr(db_school, field, value)

    db.commit()
    db.refresh(db_school)
    return db_school


@router.delete("/{school_id}")
def delete_school(school_id: int, soft: bool = True, db: Session = Depends(get_db)):
    """Delete a school (soft delete by default)"""
    db_school = db.query(School).filter(School.id == school_id).first()
    if not db_school:
        raise HTTPException(status_code=404, detail="School not found")

    if soft:
        db_school.is_deleted = True
        db_school.deleted_at = int(time.time() * 1000)
        db_school.updated_at = int(time.time() * 1000)
        db.commit()
        return {"message": "School soft deleted successfully"}
    else:
        db.delete(db_school)
        db.commit()
        return {"message": "School permanently deleted"}


@router.post("/{school_id}/restore")
def restore_school(school_id: int, db: Session = Depends(get_db)):
    """Restore a soft-deleted school"""
    db_school = db.query(School).filter(School.id == school_id).first()
    if not db_school:
        raise HTTPException(status_code=404, detail="School not found")

    db_school.is_deleted = False
    db_school.deleted_at = None
    db_school.updated_at = int(time.time() * 1000)
    db.commit()
    db.refresh(db_school)
    return db_school
