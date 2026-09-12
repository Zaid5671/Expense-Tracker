from sqlalchemy import Column, Integer, String, Numeric, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class Expense(Base):
    __tablename__ = "expenses"

    expense_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    # SET NULL so deleting a category doesn't delete the expense
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="SET NULL"), nullable=True)
    
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String, nullable=True)
    expense_date = Column(Date, nullable=False)
    is_deleted = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")
