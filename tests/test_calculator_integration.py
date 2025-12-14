"""Integration tests for calculator endpoints with authentication."""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set testing environment before importing app
os.environ["TESTING"] = "1"

from src.main import app
from src.database import Base, get_db
from src.models import User
from src.calculation_model import Calculation
from src.security import hash_password

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_calculator.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database and tables."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create test client with database override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("testpassword123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_token(client, test_user):
    """Get authentication token for test user."""
    response = client.post(
        "/login",
        json={"username": "testuser", "password": "testpassword123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


class TestAuthenticationEndpoints:
    """Tests for authentication endpoints."""
    
    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/login",
            json={"username": "testuser", "password": "testpassword123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post(
            "/login",
            json={"username": "testuser", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user."""
        response = client.post(
            "/login",
            json={"username": "nonexistent", "password": "password"}
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client, auth_token, test_user):
        """Test getting current user with valid token."""
        response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "password_hash" not in data
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = client.get(
            "/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


class TestCalculatorEndpoints:
    """Tests for calculator endpoints."""
    
    def test_add_operation(self, client, auth_token):
        """Test addition operation."""
        response = client.post(
            "/calculator",
            json={"operation": "add", "operand1": 5.5, "operand2": 3.2},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "add"
        assert data["operand1"] == 5.5
        assert data["operand2"] == 3.2
        assert data["result"] == 8.7
    
    def test_subtract_operation(self, client, auth_token):
        """Test subtraction operation."""
        response = client.post(
            "/calculator",
            json={"operation": "subtract", "operand1": 10, "operand2": 4},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 6
    
    def test_multiply_operation(self, client, auth_token):
        """Test multiplication operation."""
        response = client.post(
            "/calculator",
            json={"operation": "multiply", "operand1": 6, "operand2": 7},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 42
    
    def test_divide_operation(self, client, auth_token):
        """Test division operation."""
        response = client.post(
            "/calculator",
            json={"operation": "divide", "operand1": 15, "operand2": 3},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 5
    
    def test_divide_by_zero(self, client, auth_token):
        """Test division by zero error."""
        response = client.post(
            "/calculator",
            json={"operation": "divide", "operand1": 10, "operand2": 0},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 400
        assert "Cannot divide by zero" in response.json()["detail"]
    
    def test_invalid_operation(self, client, auth_token):
        """Test invalid operation."""
        response = client.post(
            "/calculator",
            json={"operation": "modulo", "operand1": 10, "operand2": 3},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 400
        assert "Invalid operation" in response.json()["detail"]
    
    def test_calculator_without_auth(self, client):
        """Test calculator endpoint without authentication."""
        response = client.post(
            "/calculator",
            json={"operation": "add", "operand1": 5, "operand2": 3}
        )
        assert response.status_code == 401
    
    def test_case_insensitive_operations(self, client, auth_token):
        """Test that operations are case-insensitive."""
        response = client.post(
            "/calculator",
            json={"operation": "ADD", "operand1": 2, "operand2": 3},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert response.json()["result"] == 5


class TestCalculationHistory:
    """Tests for calculation history endpoints."""
    
    def test_get_empty_history(self, client, auth_token):
        """Test getting empty calculation history."""
        response = client.get(
            "/calculator/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert response.json() == []
    
    def test_calculation_saved_to_history(self, client, auth_token, db, test_user):
        """Test that calculations are saved to history."""
        # Perform calculation
        client.post(
            "/calculator",
            json={"operation": "add", "operand1": 5, "operand2": 3},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Check history
        response = client.get(
            "/calculator/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        history = response.json()
        assert len(history) == 1
        assert history[0]["operation"] == "add"
        assert history[0]["operand1"] == 5
        assert history[0]["operand2"] == 3
        assert history[0]["result"] == 8
    
    def test_multiple_calculations_history(self, client, auth_token):
        """Test multiple calculations in history."""
        # Perform multiple calculations
        client.post(
            "/calculator",
            json={"operation": "add", "operand1": 5, "operand2": 3},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        client.post(
            "/calculator",
            json={"operation": "multiply", "operand1": 4, "operand2": 6},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Check history
        response = client.get(
            "/calculator/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        history = response.json()
        assert len(history) == 2
        # History should be ordered by created_at desc (most recent first)
        # Check that both operations are present
        operations = {h["operation"] for h in history}
        assert "add" in operations
        assert "multiply" in operations
    
    def test_history_pagination(self, client, auth_token):
        """Test history pagination."""
        # Create 5 calculations
        for i in range(5):
            client.post(
                "/calculator",
                json={"operation": "add", "operand1": i, "operand2": 1},
                headers={"Authorization": f"Bearer {auth_token}"}
            )
        
        # Get first 2
        response = client.get(
            "/calculator/history?skip=0&limit=2",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 2
        
        # Get next 2
        response = client.get(
            "/calculator/history?skip=2&limit=2",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 2
    
    def test_clear_history(self, client, auth_token):
        """Test clearing calculation history."""
        # Create calculation
        client.post(
            "/calculator",
            json={"operation": "add", "operand1": 5, "operand2": 3},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Clear history
        response = client.delete(
            "/calculator/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 204
        
        # Verify history is empty
        response = client.get(
            "/calculator/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert response.json() == []
    
    def test_history_isolated_per_user(self, client, db):
        """Test that calculation history is isolated per user."""
        # Create two users
        user1 = User(
            username="user1",
            email="user1@example.com",
            password_hash=hash_password("password1")
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            password_hash=hash_password("password2")
        )
        db.add(user1)
        db.add(user2)
        db.commit()
        
        # Get tokens for both users
        token1 = client.post(
            "/login",
            json={"username": "user1", "password": "password1"}
        ).json()["access_token"]
        
        token2 = client.post(
            "/login",
            json={"username": "user2", "password": "password2"}
        ).json()["access_token"]
        
        # User 1 performs calculation
        client.post(
            "/calculator",
            json={"operation": "add", "operand1": 10, "operand2": 5},
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        # User 2 performs calculation
        client.post(
            "/calculator",
            json={"operation": "multiply", "operand1": 3, "operand2": 4},
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        # Check user 1 history
        response1 = client.get(
            "/calculator/history",
            headers={"Authorization": f"Bearer {token1}"}
        )
        assert len(response1.json()) == 1
        assert response1.json()[0]["operation"] == "add"
        
        # Check user 2 history
        response2 = client.get(
            "/calculator/history",
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert len(response2.json()) == 1
        assert response2.json()[0]["operation"] == "multiply"
