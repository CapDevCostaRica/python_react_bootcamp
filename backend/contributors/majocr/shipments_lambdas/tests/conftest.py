import pytest
from app.common.python.common.authentication.jwt import encode_jwt
from main import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

@pytest.fixture
def mock_context_session(mocker):
    mock_user = mocker.Mock()
    mock_user.id = 1
    mock_user.role = "carrier"
    mock_user.warehouse_id = 42
    mock_user.store_id = None
    mock_user.carrier_id = None

    mock_session = mocker.Mock()
    mock_session.query().filter().first.return_value = mock_user

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.login.src.app.get_session", return_value=mock_context)
    return mock_user

def with_user_role(role="global_manager", carrier_id=None, warehouse_id=None, store_id=None):
    def decorator(test_func):
        def wrapper(client, mocker, *args, **kwargs):
            mock_user = mocker.Mock()
            mock_user.id = 1
            mock_user.role = role
            mock_user.carrier_id = carrier_id
            mock_user.warehouse_id = warehouse_id
            mock_user.store_id = store_id

            mock_session = mocker.Mock()
            mock_session.query().filter().first.return_value = mock_user

            mock_context = mocker.MagicMock()
            mock_context.__enter__.return_value = mock_session
            mock_context.__exit__.return_value = None

            mocker.patch("app.functions.login.src.app.get_session", return_value=mock_context)
            return test_func(client, mock_user, *args, **kwargs)
        return wrapper
    return decorator

def generate_token(role="global_manager", **kwargs):
    payload = {
        "sub": 1,
        "role": role,
        **kwargs
    }
    return f"Bearer {encode_jwt(payload)}"
