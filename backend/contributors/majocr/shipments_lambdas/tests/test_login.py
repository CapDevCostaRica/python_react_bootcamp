import json
import pytest
from http import HTTPStatus, client
from main import app
from app.functions.login.src.app import handler as login_handler
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

@pytest.fixture
def mock_session():
    with patch("app.functions.login.src.app.get_session") as mock_get_session:
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.role = "carrier"
        mock_user.warehouse_id = 42
        mock_db.query().filter().first.return_value = mock_user
        mock_get_session.return_value.__enter__.return_value = mock_db
        yield mock_get_session

# 1. Successful login with valid username
def test_successful_login_with_valid_username(client, mock_session):
    response = client.post("/login", json={"username": "Carrier1"})
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"

# 2. Failed login with invalid username
@pytest.fixture
def mock_invalid_user():
    with patch("app.functions.login.src.app.get_session") as mock_get_session:
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None
        mock_get_session.return_value.__enter__.return_value = mock_db
        yield mock_get_session

def test_failed_login_with_invalid_username(client, mock_invalid_user):
    response = client.post("/login", json={"username": "NoSuchUser"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid credentials"

# 3. Failed login with missing username
def test_failed_login_with_missing_username(client):
    response = client.post("/login", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "username" in data["error"]
