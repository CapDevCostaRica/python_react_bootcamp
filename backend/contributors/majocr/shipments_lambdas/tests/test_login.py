import pytest
from app.common.python.common.authentication.jwt import decode_jwt

# 1. Successful login with valid username
def test_successful_login_with_valid_username(client, mock_context_session):
    response = client.post("/login", json={"username": "Carrier1"})
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"

# 2. Failed login with invalid username
def test_failed_login_with_invalid_username(client, mocker):
    mock_session = mocker.Mock()
    mock_session.query().filter().first.return_value = None
    
    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.login.src.app.get_session", return_value=mock_context)

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
