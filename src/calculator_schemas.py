"""Pydantic schemas for calculator operations."""
from pydantic import BaseModel, Field
from datetime import datetime


class CalculationRequest(BaseModel):
    """Schema for calculator operation request."""
    
    operation: str = Field(..., description="Operation: add, subtract, multiply, divide")
    operand1: float = Field(..., description="First number")
    operand2: float = Field(..., description="Second number")


class CalculationResponse(BaseModel):
    """Schema for calculator operation response."""
    
    operation: str
    operand1: float
    operand2: float
    result: float
    message: str
    
    model_config = {"from_attributes": True}


class CalculationHistory(BaseModel):
    """Schema for calculation history."""
    
    id: int
    operation: str
    operand1: float
    operand2: float
    result: float
    created_at: datetime
    
    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema for authentication token."""
    
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    """Schema for login request."""
    
    username: str
    password: str
