from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import FeeRecord
from app.schemas import FeeRecordCreate, FeeRecordResponse, timestamp_to_datetime
from app.utils.timezone import now_ist

router = APIRouter()


@router.get("/", response_model=List[FeeRecordResponse])
def get_fee_records(
    skip: int = 0,
    limit: int = 100,
    student_id: int = None,
    db: Session = Depends(get_db)
):
    """Get all fee records"""
    query = db.query(FeeRecord).filter(FeeRecord.is_deleted == False)
    if student_id:
        query = query.filter(FeeRecord.student_id == student_id)
    fee_records = query.offset(skip).limit(limit).all()
    return fee_records


@router.get("/{fee_record_id}", response_model=FeeRecordResponse)
def get_fee_record(fee_record_id: int, db: Session = Depends(get_db)):
    """Get a specific fee record by ID"""
    fee_record = db.query(FeeRecord).filter(FeeRecord.id == fee_record_id).first()
    if not fee_record:
        raise HTTPException(status_code=404, detail="Fee record not found")
    return fee_record


@router.get("/receipt/{receipt_id}", response_model=FeeRecordResponse)
def get_fee_record_by_receipt(receipt_id: str, db: Session = Depends(get_db)):
    """Get a fee record by receipt ID"""
    fee_record = db.query(FeeRecord).filter(FeeRecord.receipt_id == receipt_id).first()
    if not fee_record:
        raise HTTPException(status_code=404, detail="Fee record not found")
    return fee_record


@router.post("/", response_model=FeeRecordResponse, status_code=status.HTTP_201_CREATED)
def create_fee_record(fee_record: FeeRecordCreate, db: Session = Depends(get_db)):
    """Create a new fee record"""
    # Check if receipt ID already exists
    existing = db.query(FeeRecord).filter(FeeRecord.receipt_id == fee_record.receipt_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Receipt ID already exists")

    # Convert timestamp to datetime for date field
    fee_data = fee_record.model_dump(exclude={"device_id"})
    fee_data["date"] = timestamp_to_datetime(fee_record.date)

    db_fee_record = FeeRecord(
        **fee_data,
        device_id=fee_record.device_id,
        last_synced_at=now_ist()
        # created_at uses default from model
    )
    db.add(db_fee_record)
    db.commit()
    db.refresh(db_fee_record)
    return db_fee_record
