from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class ExpenseBase(BaseModel):
    # Field(gt=0) ensures the API rejects any amount less than or equal to 0
    amount: Decimal = Field(gt=0, description="Amount must be greater than zero")
    category_id: Optional[int] = None
    description: Optional[str] = None
    expense_date: date

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    category_id: Optional[int] = None
    description: Optional[str] = None
    expense_date: Optional[date] = None

class ExpenseResponse(ExpenseBase):
    expense_id: int
    user_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
