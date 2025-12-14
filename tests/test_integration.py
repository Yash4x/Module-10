"""Integration tests for the FastAPI application."""
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base, get_db

# Set testing environment variable
os.environ["TESTING"] = "1"

# Import app after setting environment variable
import src.main

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create a test client with database override."""
    # Override the database dependency
    src.main.app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    with TestClient(src.main.app, raise_server_exceptions=True) as test_client:
        yield test_client
    
    # Clean up
    src.main.app.dependency_overrides.clear()


class TestRootEndpoints:
    """Test root and health endpoints."""
    
    def test_read_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestUserCreation:
    """Test user creation endpoint."""
    
    def test_create_user_success(self, client):
        """Test successful user creation."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert data["user"]["username"] == "testuser"
        assert data["user"]["email"] == "test@example.com"
        assert "password" not in data["user"]
        assert "password_hash" not in data["user"]
        assert "created_at" in data["user"]
    
    def test_create_user_duplicate_username(self, client):
        """Test creating user with duplicate username."""
        user_data = {
            "username": "testuser",
            "email": "test1@example.com",
            "password": "securepass123"
        }
        # Create first user
        response1 = client.post("/users", json=user_data)
        assert response1.status_code == 201
        
        # Try to create user with same username but different email
        user_data2 = {
            "username": "testuser",
            "email": "test2@example.com",
            "password": "securepass456"
        }
        response2 = client.post("/users", json=user_data2)
        assert response2.status_code == 400
        assert "username" in response2.json()["detail"].lower()
    
    def test_create_user_duplicate_email(self, client):
        """Test creating user with duplicate email."""
        user_data = {
            "username": "testuser1",
            "email": "test@example.com",
            "password": "securepass123"
        }
        # Create first user
        response1 = client.post("/users", json=user_data)
        assert response1.status_code == 201
        
        # Try to create user with different username but same email
        user_data2 = {
            "username": "testuser2",
            "email": "test@example.com",
            "password": "securepass456"
        }
        response2 = client.post("/users", json=user_data2)
        assert response2.status_code == 400
        assert "email" in response2.json()["detail"].lower()
    
    def test_create_user_invalid_email(self, client):
        """Test creating user with invalid email format."""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "securepass123"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_user_short_password(self, client):
        """Test creating user with password too short."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "short"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_user_short_username(self, client):
        """Test creating user with username too short."""
        user_data = {
            "username": "ab",
            "email": "test@example.com",
            "password": "securepass123"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 422  # Validation error


class TestUserRetrieval:
    """Test user retrieval endpoints."""
    
    def test_get_user_by_id(self, client):
        """Test getting a user by ID."""
        # Create a user first
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123"
        }
        create_response = client.post("/users", json=user_data)
        user_id = create_response.json()["user"]["id"]
        
        # Get the user
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "password" not in data
        assert "password_hash" not in data
    
    def test_get_user_not_found(self, client):
        """Test getting a user that doesn't exist."""
        response = client.get("/users/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_list_users(self, client):
        """Test listing all users."""
        # Create multiple users
        users_data = [
            {"username": "user1", "email": "user1@example.com", "password": "password123"},
            {"username": "user2", "email": "user2@example.com", "password": "password123"},
            {"username": "user3", "email": "user3@example.com", "password": "password123"}
        ]
        for user_data in users_data:
            client.post("/users", json=user_data)
        
        # List users
        response = client.get("/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("password" not in user for user in data)
        assert all("password_hash" not in user for user in data)
    
    def test_list_users_pagination(self, client):
        """Test listing users with pagination."""
        # Create multiple users
        for i in range(5):
            user_data = {
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "password": "password123"
            }
            client.post("/users", json=user_data)
        
        # Test with limit
        response = client.get("/users?limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2
        
        # Test with skip
        response = client.get("/users?skip=2&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestUserDeletion:
    """Test user deletion endpoint."""
    
    def test_delete_user(self, client):
        """Test deleting a user."""
        # Create a user first
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123"
        }
        create_response = client.post("/users", json=user_data)
        user_id = create_response.json()["user"]["id"]
        
        # Delete the user
        response = client.delete(f"/users/{user_id}")
        assert response.status_code == 204
        
        # Verify user is deleted
        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == 404
    
    def test_delete_user_not_found(self, client):
        """Test deleting a user that doesn't exist."""
        response = client.delete("/users/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
