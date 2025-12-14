"""Unit tests for password hashing and validation."""
import pytest
from src.security import hash_password, verify_password


class TestPasswordHashing:
    """Test password hashing functionality."""
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        password = "test_password123"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
    
    def test_hash_password_different_from_original(self):
        """Test that hashed password is different from original."""
        password = "test_password123"
        hashed = hash_password(password)
        assert hashed != password
    
    def test_hash_password_produces_unique_hashes(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "test_password123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        # Hashes should be different due to different salts
        assert hash1 != hash2
    
    def test_verify_password_correct_password(self):
        """Test that verify_password returns True for correct password."""
        password = "test_password123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect_password(self):
        """Test that verify_password returns False for incorrect password."""
        password = "test_password123"
        wrong_password = "wrong_password456"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty_password(self):
        """Test verify_password with empty password."""
        password = "test_password123"
        hashed = hash_password(password)
        assert verify_password("", hashed) is False


class TestSchemaValidation:
    """Test Pydantic schema validation."""
    
    def test_user_create_valid_data(self):
        """Test UserCreate with valid data."""
        from src.schemas import UserCreate
        
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123"
        }
        user = UserCreate(**user_data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "securepass123"
    
    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email."""
        from src.schemas import UserCreate
        from pydantic import ValidationError
        
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "securepass123"
        }
        with pytest.raises(ValidationError):
            UserCreate(**user_data)
    
    def test_user_create_short_username(self):
        """Test UserCreate with username too short."""
        from src.schemas import UserCreate
        from pydantic import ValidationError
        
        user_data = {
            "username": "ab",  # Less than 3 characters
            "email": "test@example.com",
            "password": "securepass123"
        }
        with pytest.raises(ValidationError):
            UserCreate(**user_data)
    
    def test_user_create_short_password(self):
        """Test UserCreate with password too short."""
        from src.schemas import UserCreate
        from pydantic import ValidationError
        
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "short"  # Less than 8 characters
        }
        with pytest.raises(ValidationError):
            UserCreate(**user_data)
    
    def test_user_read_excludes_password(self):
        """Test that UserRead schema doesn't include password_hash."""
        from src.schemas import UserRead
        
        # UserRead should not have password or password_hash fields
        assert "password" not in UserRead.model_fields
        assert "password_hash" not in UserRead.model_fields
        assert "username" in UserRead.model_fields
        assert "email" in UserRead.model_fields
