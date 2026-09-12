from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from database import get_db
from models.expense import Expense
from models.category import Category
from models.user import User
from schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/expenses", tags=["Expenses"])

@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense: ExpenseCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify the category exists and belongs to the user or is a system default
    if expense.category_id:
        category = db.query(Category).filter(
            Category.category_id == expense.category_id,
            ((Category.user_id == None) | (Category.user_id == current_user.user_id))
        ).first()
        
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category")
            
    new_expense = Expense(
        user_id=current_user.user_id,
        category_id=expense.category_id,
        amount=expense.amount,
        description=expense.description,
        expense_date=expense.expense_date
    )
    
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    
    return new_expense

@router.get("/", response_model=List[ExpenseResponse])
def get_expenses(
    start_date: Optional[date] = Query(None, description="Filter from this date"),
    end_date: Optional[date] = Query(None, description="Filter to this date"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Start the query, filtering ONLY this user's expenses and ignoring soft-deleted ones
    query = db.query(Expense).filter(
        Expense.user_id == current_user.user_id,
        Expense.is_deleted == False
    )
    
    # Apply date filters if they exist
    if start_date:
        query = query.filter(Expense.expense_date >= start_date)
    if end_date:
        query = query.filter(Expense.expense_date <= end_date)
        
    # Apply pagination and execute, ordering by newest first
    expenses = query.order_by(Expense.expense_date.desc()).offset(offset).limit(limit).all()
    
    return expenses

@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = db.query(Expense).filter(
        Expense.expense_id == expense_id,
        Expense.user_id == current_user.user_id,
        Expense.is_deleted == False
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
        
    return expense

@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int, 
    expense_update: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = db.query(Expense).filter(
        Expense.expense_id == expense_id,
        Expense.user_id == current_user.user_id,
        Expense.is_deleted == False
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
        
    # Verify category if it's being updated
    if expense_update.category_id is not None:
        category = db.query(Category).filter(
            Category.category_id == expense_update.category_id,
            ((Category.user_id == None) | (Category.user_id == current_user.user_id))
        ).first()
        
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category")
            
    # Update fields that were provided (Pydantic v2 syntax)
    update_data = expense_update.model_dump(exclude_unset=True) 
    for key, value in update_data.items():
        setattr(expense, key, value)
        
    db.commit()
    db.refresh(expense)
    
    return expense

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = db.query(Expense).filter(
        Expense.expense_id == expense_id,
        Expense.user_id == current_user.user_id,
        Expense.is_deleted == False
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
        
    # Soft Delete!
    expense.is_deleted = True
    db.commit()
    
    return None
