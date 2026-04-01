from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Expense
from app.schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse, BulkExpenseCreate
from app.auth import get_current_user
import time

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


@router.get("/", response_model=List[ExpenseResponse])
def get_expenses(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all expenses with optional filtering"""
    query = db.query(Expense).filter(Expense.is_deleted == False)

    if category:
        query = query.filter(Expense.category == category)

    if start_date:
        query = query.filter(Expense.expense_date >= start_date)

    if end_date:
        query = query.filter(Expense.expense_date <= end_date)

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
    current_time = int(time.time() * 1000)

    db_expense = Expense(
        category=expense.category,
        description=expense.description,
        amount=expense.amount,
        expense_date=expense.expense_date,
        payment_method=expense.payment_method,
        vendor_name=expense.vendor_name,
        receipt_number=expense.receipt_number,
        notes=expense.notes,
        device_id=expense.device_id,
        created_at=current_time,
        updated_at=current_time,
        last_synced_at=current_time
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
    if not update_data.get("updated_at"):
        update_data["updated_at"] = int(time.time() * 1000)

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
        db_expense.deleted_at = int(time.time() * 1000)

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
    db_expense.updated_at = int(time.time() * 1000)

    db.commit()
    return {"message": "Expense restored successfully"}


@router.post("/bulk", response_model=List[ExpenseResponse])
def create_bulk_expenses(
    bulk_data: BulkExpenseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create multiple expenses in a single request"""
    current_time = int(time.time() * 1000)
    db_expenses = []

    for expense in bulk_data.expenses:
        db_expense = Expense(
            category=expense.category,
            description=expense.description,
            amount=expense.amount,
            expense_date=expense.expense_date,
            payment_method=expense.payment_method,
            vendor_name=expense.vendor_name,
            receipt_number=expense.receipt_number,
            notes=expense.notes,
            device_id=expense.device_id,
            created_at=current_time,
            updated_at=current_time,
            last_synced_at=current_time
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

    if start_date:
        query = query.filter(Expense.expense_date >= start_date)

    if end_date:
        query = query.filter(Expense.expense_date <= end_date)

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
