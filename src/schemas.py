"""Pydantic schemas for data validation."""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    
    username: str = Field(..., min_length=3, max_length=50, description="Username for the account")
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., min_length=8, description="Password for the account")


class UserRead(BaseModel):
    """Schema for reading user data (excludes password_hash)."""
    
    id: int
    username: str
    email: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """Schema for user response with message."""
    
    message: str
    user: UserRead
