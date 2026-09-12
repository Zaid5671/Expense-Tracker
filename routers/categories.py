from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.category import Category
from models.user import User
from schemas.category import CategoryCreate, CategoryResponse
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/categories", tags=["Categories"])

@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Fetch system default categories (user_id is None) AND this specific user's custom categories
    categories = db.query(Category).filter(
        (Category.user_id == None) | (Category.user_id == current_user.user_id)
    ).all()
    
    return categories

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Prevent duplicate categories by checking if a system default or user custom category with the same name exists
    existing = db.query(Category).filter(
        Category.name.ilike(category.name), # ilike is case-insensitive (e.g., "Food" == "food")
        ((Category.user_id == None) | (Category.user_id == current_user.user_id))
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
        
    new_category = Category(
        name=category.name,
        user_id=current_user.user_id # Because this isn't None, it belongs exclusively to this user!
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return new_category
