from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import Expense
from app.schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse, BulkExpenseCreate, timestamp_to_datetime
from app.auth import get_current_user
from app.utils.timezone import now_ist

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


@router.get("/", response_model=List[ExpenseResponse])
def get_expenses(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all expenses with optional filtering and search"""
    query = db.query(Expense).filter(Expense.is_deleted == False)

    if category:
        query = query.filter(Expense.category == category)

    # Convert timestamp parameters to datetime for comparison
    if start_date:
        start_dt = timestamp_to_datetime(start_date)
        query = query.filter(Expense.expense_date >= start_dt)

    if end_date:
        end_dt = timestamp_to_datetime(end_date)
        query = query.filter(Expense.expense_date <= end_dt)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Expense.category.ilike(search_pattern)) |
            (Expense.description.ilike(search_pattern)) |
            (Expense.vendor_name.ilike(search_pattern)) |
            (Expense.receipt_number.ilike(search_pattern))
        )

    return query.order_by(Expense.expense_date.desc()).offset(skip).limit(limit).all()


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific expense by ID"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.post("/", response_model=ExpenseResponse, status_code=201)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new expense"""
    # Convert timestamp to datetime for expense_date
    db_expense = Expense(
        category=expense.category,
        description=expense.description,
        amount=expense.amount,
        expense_date=timestamp_to_datetime(expense.expense_date),
        payment_method=expense.payment_method,
        vendor_name=expense.vendor_name,
        receipt_number=expense.receipt_number,
        notes=expense.notes,
        device_id=expense.device_id,
        last_synced_at=now_ist()
        # created_at and updated_at use defaults from model
    )

    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing expense"""
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    update_data = expense.dict(exclude_unset=True)

    # Convert timestamp fields to datetime
    if "expense_date" in update_data and update_data["expense_date"] is not None:
        update_data["expense_date"] = timestamp_to_datetime(update_data["expense_date"])
    if "deleted_at" in update_data and update_data["deleted_at"] is not None:
        update_data["deleted_at"] = timestamp_to_datetime(update_data["deleted_at"])
    if "updated_at" in update_data and update_data["updated_at"] is not None:
        update_data["updated_at"] = timestamp_to_datetime(update_data["updated_at"])
    else:
        update_data["updated_at"] = now_ist()

    for key, value in update_data.items():
        setattr(db_expense, key, value)

    db.commit()
    db.refresh(db_expense)
    return db_expense


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    hard_delete: bool = Query(False, description="Permanently delete the expense"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete an expense (soft delete by default)"""
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if hard_delete:
        db.delete(db_expense)
    else:
        db_expense.is_deleted = True
        db_expense.deleted_at = now_ist()

    db.commit()
    return {"message": "Expense deleted successfully"}


@router.post("/{expense_id}/restore")
def restore_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Restore a soft-deleted expense"""
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db_expense.is_deleted = False
    db_expense.deleted_at = None
    db_expense.updated_at = now_ist()

    db.commit()
    return {"message": "Expense restored successfully"}


@router.post("/bulk", response_model=List[ExpenseResponse])
def create_bulk_expenses(
    bulk_data: BulkExpenseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create multiple expenses in a single request"""
    db_expenses = []

    for expense in bulk_data.expenses:
        db_expense = Expense(
            category=expense.category,
            description=expense.description,
            amount=expense.amount,
            expense_date=timestamp_to_datetime(expense.expense_date),
            payment_method=expense.payment_method,
            vendor_name=expense.vendor_name,
            receipt_number=expense.receipt_number,
            notes=expense.notes,
            device_id=expense.device_id,
            last_synced_at=now_ist()
            # created_at and updated_at use defaults from model
        )
        db_expenses.append(db_expense)

    db.add_all(db_expenses)
    db.commit()
    for expense in db_expenses:
        db.refresh(expense)

    return db_expenses


@router.get("/summary/stats")
def get_expense_stats(
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get expense statistics"""
    query = db.query(Expense).filter(Expense.is_deleted == False)

    # Convert timestamp parameters to datetime for comparison
    if start_date:
        start_dt = timestamp_to_datetime(start_date)
        query = query.filter(Expense.expense_date >= start_dt)

    if end_date:
        end_dt = timestamp_to_datetime(end_date)
        query = query.filter(Expense.expense_date <= end_dt)

    expenses = query.all()

    total_amount = sum(e.amount for e in expenses)

    # Group by category
    by_category = {}
    for expense in expenses:
        if expense.category not in by_category:
            by_category[expense.category] = {"count": 0, "total": 0.0}
        by_category[expense.category]["count"] += 1
        by_category[expense.category]["total"] += expense.amount

    return {
        "total_expenses": len(expenses),
        "total_amount": total_amount,
        "by_category": by_category
    }
