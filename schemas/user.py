from pydantic import BaseModel, EmailStr
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    name: str
    email: EmailStr

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to return to client
class UserResponse(UserBase):
    user_id: int
    is_admin: bool
    created_at: datetime

    # Tells Pydantic to read data even if it is an ORM model (SQLAlchemy)
    model_config = {"from_attributes": True}
