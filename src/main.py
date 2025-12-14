"""Main FastAPI application."""
from contextlib import asynccontextmanager
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os
from src.database import get_db, Base
from src.models import User
from src.calculation_model import Calculation
from src.schemas import UserCreate, UserRead, UserResponse
from src.calculator_schemas import (
    CalculationRequest, CalculationResponse, CalculationHistory,
    Token, LoginRequest
)
from src.security import hash_password
from src.auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from src.calculator.operations import add, subtract, multiply, divide


def create_app():
    """Application factory for creating FastAPI app."""
    from src.database import engine
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Lifespan context manager for startup and shutdown events."""
        # Skip database creation in test mode
        if not os.getenv("TESTING"):
            Base.metadata.create_all(bind=engine)
        yield
        # Shutdown: Clean up (if needed)
    
    app_instance = FastAPI(
        title="Calculator API with User Authentication",
        description="A FastAPI calculator application with user authentication and calculation history",
        version="2.0.0",
        lifespan=lifespan
    )
    
    return app_instance


app = create_app()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root_api():
    """Root endpoint."""
    return {
        "message": "Welcome to Calculator API with User Authentication",
        "version": "2.0.0",
        "features": [
            "User Registration & Authentication",
            "JWT Token-based Security",
            "Calculator Operations (add, subtract, multiply, divide)",
            "Calculation History Tracking"
        ],
        "docs": "/docs",
        "endpoints": {
            "auth": ["/users", "/login", "/me"],
            "calculator": ["/calculator", "/calculator/history"]
        }
    }


@app.get("/app")
def read_root():
    """Serve the web interface."""
    return FileResponse('static/index.html')


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Calculator API",
        "version": "2.0.0"
    }


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    
    Args:
        user: User creation data
        db: Database session
        
    Returns:
        Created user data
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Hash the password
    hashed_password = hash_password(user.password)
    
    # Create new user instance
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return UserResponse(
            message="User created successfully",
            user=UserRead.model_validate(db_user)
        )
    except IntegrityError as e:
        db.rollback()
        if "username" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        elif "email" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User creation failed"
            )


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a user by ID.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        User data
        
    Raises:
        HTTPException: If user not found
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserRead.model_validate(db_user)


@app.get("/users", response_model=list[UserRead])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all users with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of users
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserRead.model_validate(user) for user in users]


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by ID.
    
    Args:
        user_id: User ID
        db: Database session
        
    Raises:
        HTTPException: If user not found
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db.delete(db_user)
    db.commit()
    return None


# ==================== Authentication Endpoints ====================

@app.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login endpoint - authenticate user and return JWT token.
    
    Args:
        login_data: Username and password
        db: Database session
        
    Returns:
        Access token for authenticated requests
        
    Raises:
        HTTPException: If authentication fails
    """
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user.
    
    Args:
        current_user: Current authenticated user from JWT token
        
    Returns:
        Current user data
    """
    return UserRead.model_validate(current_user)


# ==================== Calculator Endpoints ====================

@app.post("/calculator", response_model=CalculationResponse)
async def calculate(
    calc_request: CalculationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform a calculation (protected endpoint - requires authentication).
    
    Args:
        calc_request: Calculation operation and operands
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Calculation result
        
    Raises:
        HTTPException: If operation is invalid or division by zero
    """
    operation = calc_request.operation.lower()
    a = calc_request.operand1
    b = calc_request.operand2
    
    # Perform calculation based on operation
    try:
        if operation == "add":
            result = add(a, b)
        elif operation == "subtract":
            result = subtract(a, b)
        elif operation == "multiply":
            result = multiply(a, b)
        elif operation == "divide":
            result = divide(a, b)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid operation: {operation}. Use: add, subtract, multiply, divide"
            )
    except ZeroDivisionError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot divide by zero"
        )
    
    # Save calculation to history
    db_calculation = Calculation(
        user_id=current_user.id,
        operation=operation,
        operand1=a,
        operand2=b,
        result=result
    )
    db.add(db_calculation)
    db.commit()
    
    return CalculationResponse(
        operation=operation,
        operand1=a,
        operand2=b,
        result=result,
        message=f"Successfully calculated: {a} {operation} {b} = {result}"
    )


@app.get("/calculator/history", response_model=list[CalculationHistory])
async def get_calculation_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get calculation history for the authenticated user.
    
    Args:
        current_user: Authenticated user
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of user's calculation history
    """
    calculations = db.query(Calculation).filter(
        Calculation.user_id == current_user.id
    ).order_by(Calculation.created_at.desc()).offset(skip).limit(limit).all()
    
    return [CalculationHistory.model_validate(calc) for calc in calculations]


@app.delete("/calculator/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_calculation_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear all calculation history for the authenticated user.
    
    Args:
        current_user: Authenticated user
        db: Database session
    """
    db.query(Calculation).filter(Calculation.user_id == current_user.id).delete()
    db.commit()
    return None
