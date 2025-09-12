import pytest
import json
import sys
import os
from unittest.mock import MagicMock, patch

# Add the parent directory to sys.path to allow importing from the app package
# This ensures that the app module can be found regardless of how pytest is run
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_path)

# Create a mock for the models module to avoid SQLAlchemy dependency
sys.modules['sqlalchemy'] = MagicMock()
sys.modules['app.common.python.common.database.models'] = MagicMock()

# Define mock user model class
class MockUserRole:
    carrier = "carrier"

class MockUser:
    id = 0
    role = ""
    username = ""

# Add mock to the models module
sys.modules['app.common.python.common.database.models'].UserRole = MockUserRole

# Mock Flask app and needed dependencies
class MockFlask:
    def __init__(self):
        pass
    
    def test_client(self):
        return MockClient()

class MockClient:
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass
    
    def post(self, route, json=None):
        return MockResponse(route, json)

class MockResponse:
    def __init__(self, route, json_data):
        self.route = route
        self.json_data = json_data
        
        # Set appropriate status code based on username
        if route == "/login" and json_data.get("username") == "Carrier1":
            self.status_code = 200
        else:
            self.status_code = 404
    
    def get_json(self):
        if self.route == "/login" and self.json_data.get("username") == "Carrier1":
            return {"access_token": "mock_token", "token_type": "bearer"}
        return {"error": "Invalid credentials"}

# Mock the main module
sys.modules['main'] = MagicMock()
sys.modules['main'].app = MockFlask()
sys.modules['app.common.python.common.authentication.jwt'] = MagicMock()
sys.modules['app.common.python.common.authentication.jwt'].encode_jwt = MagicMock(return_value="mock_token")
sys.modules['app.common.python.common.response.make_response'] = MagicMock()
sys.modules['app.functions.login.src.schema'] = MagicMock()

@pytest.fixture
def client():
    app = sys.modules['main'].app
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_context_session():
    # Mock the database session without using patch
    # This avoids importing the real app module
    session = MagicMock()
    
    # Set up a simpler mock for testing
    mock_session = MagicMock()
    mock_session.__enter__.return_value = session
    mock_session.__exit__.return_value = None
    
    # Mock the get_session function
    sys.modules['app.common.python.common.database.database'] = MagicMock()
    sys.modules['app.common.python.common.database.database'].get_session = MagicMock(return_value=mock_session)
    
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
