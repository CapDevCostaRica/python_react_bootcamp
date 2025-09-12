import pytest
import json
from http import HTTPStatus
from unittest.mock import MagicMock
from app.functions.shipment.shipment_create.src.app import handler
from app.common.python.common.database.models import UserRole as ur

@pytest.fixture
def base_event():
    return {
        "body": None,
        "isBase64Enconded": False,
        "claims": {
            "id": 1,
            "role": ur.warehouse_staff
        }
    }

@pytest.fixture
def mock_session(mocker):
    session = mocker.MagicMock()
    mocker.patch("app.common.python.common.database.database.get_session", return_value=session)
    return session

@pytest.fixture
def valid_body():
    return {
        "origin_warehouse": 1,
        "target_warehouse": 2,
        "carrier": 99,
        "status": "created",
        "shipment_locations": ["12345", "54321"]
    }

# 1. Successful shipment create
def test_create_valid_shipment(base_event, mock_session, valid_body):
    base_event["body"] = json.dumps(valid_body)
    mock_session().__enter__().query().filter_by(id=1).first.return_value = MagicMock(warehouse_id=1)
    mock_session().__enter__().query().filter_by(id=2).first.return_value = MagicMock()
    response = handler(base_event, {})
    assert response["statusCode"] == HTTPStatus.OK

# 2. Failed shipment creation because of origin and target warehouses are the same
def test_origin_equals_target_warehouse(base_event, valid_body):
    valid_body["target_warehouse"] = 1
    base_event["body"] = json.dumps(valid_body)
    response = handler(base_event, {})
    assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert "Origin and destination cannot be the same" in response["body"]

# 3. Failed shipment creation because of missing required fields
def test_missing_required_fields(base_event):
    base_event["body"] = json.dumps({})
    response = handler(base_event, {})
    assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert "Invalid JSON body" in response["body"]

# 4. Failed shipment creation because of some or both of the warehouses does not exist
def test_invalid_origin_or_destination_warehouse_id(base_event, mock_session, valid_body):
    base_event["body"] = json.dumps(valid_body)
    mock_session().__enter__().query().filter_by(id=1).first.return_value = MagicMock(warehouse_id=1)
    mock_session().__enter__().query().filter_by(id=2).first.return_value = None  # Destination warehouse does not exist
    response = handler(base_event, {})
    assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert "Origin and/or destination warehouses does not exist" in response["body"]

# 5. Failed shipment creation because of the user warehouse is 
def test_user_not_assigned_to_origin(base_event, mock_session, valid_body):
    base_event["body"] = json.dumps(valid_body)
    mock_session().__enter__().query().filter_by(id=1).first.return_value = MagicMock(warehouse_id=99)
    mock_session().__enter__().query().filter_by(id=2).first.return_value = MagicMock()
    response = handler(base_event, {})
    assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert "You can only start shipments from your own warehouse" in response["body"]
