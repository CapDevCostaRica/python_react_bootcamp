import pytest
import json
from http import HTTPStatus
from unittest.mock import MagicMock
from app.functions.login.src.app import handler

@pytest.fixture
def base_event():
    return {
        "body": json.dumps({"username": "valid_user"}),
        "isBase64Enconded": False
    }

@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1
    user.role = "admin"
    return user

@pytest.fixture
def mock_session(mocker):
    session = mocker.MagicMock()
    mocker.patch(
        "app.common.python.common.database.database.get_session",
        return_value=session
    )
    return session

@pytest.fixture
def mock_schema(mocker):
    schema = mocker.patch(".schema.LoginRequestSchema")
    schema.return_value.load.return_value = {"username": "valid_user"}
    return schema

@pytest.fixture
def mock_make_response(mocker):
    return mocker.patch("app.common.python.common.response.make_response.make_response")

@pytest.fixture
def mock_jwt(mocker):
    return mocker.patch(
        "app.common.python.common.authentication.jwt.encode_jwt",
        return_value="mocked-jwt"
    )

# 1. Successful login with valid username
def test_login_successful(base_event, mock_session, mock_user, mock_make_response):
    mock_session().__enter__().query().filter().first.return_value = mock_user
    handler(base_event, {})
    mock_make_response.assert_called_with(
        {"access_token": "mocked-jwt", "token_type": "Bearer"},
        HTTPStatus.OK
    )

# 2. Failed login with invalid username
def test_login_invalid_username(base_event, mock_session, mock_schema, mock_make_response):
    base_event["body"] = json.dumps({"username": "unknown_user"})
    mock_schema.return_value.load.return_value = {"username": "unknown_user"}
    mock_session().__enter__().query().filter().first.return_value = None
    handler(base_event, {})
    mock_make_response.assert_called_with(
        {"error": "Invalid credentials"},
        HTTPStatus.NOT_FOUND
    )

# 3. Failed login with missing username (invalid JSON body)
def test_login_missing_username(base_event, mocker, mock_make_response):
    base_event["body"] = json.dumps({})
    mock_schema = mocker.patch("app.functions.login.src.schema.LoginRequestSchema")
    mock_schema.return_value.load.side_effect = Exception("Missing username")
    handler(base_event, {})
    mock_make_response.assert_called_with(
        {"error": "Invalid JSON body"},
        HTTPStatus.BAD_REQUEST
    )
