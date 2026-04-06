from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import Batch
from app.schemas import BatchCreate, BatchUpdate, BatchResponse, timestamp_to_datetime
from app.utils.timezone import now_ist

router = APIRouter()


@router.get("/", response_model=List[BatchResponse])
def get_batches(
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
    search: str = None,
    db: Session = Depends(get_db)
):
    """Get all batches with optional search"""
    query = db.query(Batch)
    if not include_deleted:
        query = query.filter(Batch.is_deleted == False)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Batch.name.ilike(search_pattern)) |
            (Batch.time.ilike(search_pattern))
        )
    batches = query.offset(skip).limit(limit).all()
    return batches


@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(batch_id: int, db: Session = Depends(get_db)):
    """Get a specific batch by ID"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


@router.post("/", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(batch: BatchCreate, db: Session = Depends(get_db)):
    """Create a new batch"""
    db_batch = Batch(
        **batch.model_dump(exclude={"device_id"}),
        device_id=batch.device_id,
        last_synced_at=now_ist()
        # created_at and updated_at use defaults from model
    )
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch


@router.put("/{batch_id}", response_model=BatchResponse)
def update_batch(
    batch_id: int,
    batch: BatchUpdate,
    db: Session = Depends(get_db)
):
    """Update a batch"""
    db_batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    update_data = batch.model_dump(exclude_unset=True)

    # Convert timestamp fields to datetime
    if "deleted_at" in update_data and update_data["deleted_at"] is not None:
        update_data["deleted_at"] = timestamp_to_datetime(update_data["deleted_at"])
    if "updated_at" in update_data and update_data["updated_at"] is not None:
        update_data["updated_at"] = timestamp_to_datetime(update_data["updated_at"])
    else:
        update_data["updated_at"] = now_ist()

    update_data["last_synced_at"] = now_ist()

    for field, value in update_data.items():
        setattr(db_batch, field, value)

    db.commit()
    db.refresh(db_batch)
    return db_batch


@router.delete("/{batch_id}")
def delete_batch(batch_id: int, soft: bool = True, db: Session = Depends(get_db)):
    """Delete a batch (soft delete by default)"""
    db_batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    if soft:
        db_batch.is_deleted = True
        db_batch.deleted_at = now_ist()
        db_batch.updated_at = now_ist()
        db.commit()
        return {"message": "Batch soft deleted successfully"}
    else:
        db.delete(db_batch)
        db.commit()
        return {"message": "Batch permanently deleted"}


@router.post("/{batch_id}/restore")
def restore_batch(batch_id: int, db: Session = Depends(get_db)):
    """Restore a soft-deleted batch"""
    db_batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    db_batch.is_deleted = False
    db_batch.deleted_at = None
    db_batch.updated_at = now_ist()
    db.commit()
    db.refresh(db_batch)
    return db_batch
