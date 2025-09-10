import pytest
import json
from unittest.mock import MagicMock, patch
from app.common.python.common.database import models

@pytest.fixture
def client():
    from main import app
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_context_session():
    # Mock the database session
    with patch('app.functions.login.src.app.get_session') as mock_session:
        # Create a mock session
        session = MagicMock()
        mock_session.return_value.__enter__.return_value = session
        mock_session.return_value.__exit__.return_value = None
        yield session

def test_successful_login_with_valid_username(client, mock_context_session):
    """Test successful login with a valid username"""
    # Setup the mock user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.role = "carrier"
    mock_user.username = "Carrier1"
    
    # Configure the mock session to return our mock user
    mock_context_session.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Send the login request
    response = client.post("/login", json={"username": "Carrier1"})
    
    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_failed_login_with_invalid_username(client, mock_context_session):
    """Test failed login with an invalid username"""
    # Configure the mock session to return None (user not found)
    mock_context_session.query.return_value.filter.return_value.first.return_value = None
    
    # Send the login request with an invalid username
    response = client.post("/login", json={"username": "NonExistentUser"})
    
    # Assertions
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Invalid credentials"
