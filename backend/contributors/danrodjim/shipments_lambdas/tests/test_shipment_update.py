import pytest
from http import HTTPStatus
from unittest.mock import MagicMock
from app.functions.shipment.shipment_update.src.app import handler
from app.common.python.common.database.models import ShipmentStatus as ss, UserRole as ur

@pytest.fixture
def base_event():
    return {
        "pathParameters": {"shipment_id": "123"},
        "isBase64Enconded": False,
        "body": None,
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
def mock_shipment():
    shipment = MagicMock()
    shipment.status = ss.created
    shipment.assigned_carrier_id = 99
    return shipment

# 1. Successful update with transition of status from Created to In_transit
def test_status_created_to_in_transit_success(base_event, mock_session, mock_shipment):
    base_event["body"] = '{"status": "in_transit"}'
    mock_session().__enter__().query().filter_by().first.return_value = mock_shipment
    response = handler(base_event, {})
    assert response["statusCode"] == HTTPStatus.OK
    assert mock_shipment.status == ss.in_transit
    assert mock_shipment.in_transit_at is not None

# 2. Successful update with transition of status from In_transit to Delivered
def test_status_in_transit_to_delivered_success(base_event, mock_session, mock_shipment):
    base_event["body"] = '{"status": "delivered"}'
    mock_shipment.status = ss.in_transit
    mock_session().__enter__().query().filter_by().first.return_value = mock_shipment
    response = handler(base_event, {})
    assert response["statusCode"] == HTTPStatus.OK
    assert mock_shipment.status == ss.delivered
    assert mock_shipment.delivered_at is not None

# 3. Failed update because the new status cannot be the same that are already assigned
def test_invalid_same_status_transition(base_event, mock_session, mock_shipment):
    base_event["body"] = '{"status": "in_transit"}'
    mock_shipment.status = ss.in_transit
    mock_session().__enter__().query().filter_by().first.return_value = mock_shipment
    response = handler(base_event, {})
    assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert "already in status" in response["body"]

# 4. Failed update because cannot update the status from Created to Delivered
def test_invalid_created_to_delivered(base_event, mock_session, mock_shipment):
    base_event["body"] = '{"status": "delivered"}'
    mock_shipment.status = ss.created
    mock_session().__enter__().query().filter_by().first.return_value = mock_shipment
    response = handler(base_event, {})
    assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert "directly to 'delivered'" in response["body"]

# 5. Failed update because cannot update the status when is Delivered
def test_invalid_delivered_cannot_transition(base_event, mock_session, mock_shipment):
    base_event["body"] = '{"status": "in_transit"}'
    mock_shipment.status = ss.delivered
    mock_session().__enter__().query().filter_by().first.return_value = mock_shipment
    response = handler(base_event, {})
    assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert "Cannot change status of a delivered shipment" in response["body"]

# 6. Successful update with role of carrier, status = in_transit and location is in the request body
def test_carrier_updates_location_success(base_event, mock_session, mock_shipment):
    base_event["claims"]["role"] = ur.carrier
    base_event["claims"]["id"] = 99
    base_event["body"] = '{"location": "12345"}'
    mock_shipment.status = ss.in_transit
    mock_shipment.assigned_carrier_id = 99
    mock_session().__enter__().query().filter_by().first.return_value = mock_shipment
    response = handler(base_event, {})
    assert response["statusCode"] == HTTPStatus.OK

# 7. Failed update with role carrier because the assigned carrier is other
def test_carrier_not_assigned_forbidden(base_event, mock_session, mock_shipment):
    base_event["claims"]["role"] = ur.carrier
    base_event["claims"]["id"] = 88
    base_event["body"] = '{"location": "12345"}'
    mock_shipment.status = ss.in_transit
    mock_shipment.assigned_carrier_id = 99
    mock_session().__enter__().query().filter_by().first.return_value = mock_shipment
    response = handler(base_event, {})
    assert response["statusCode"] == HTTPStatus.FORBIDDEN
    assert "not the assigned carrier" in response["body"]

# 8. Failed update with role carrier because the shipment status is not In_transit
def test_carrier_invalid_status_for_location_update(base_event, mock_session, mock_shipment):
    base_event["claims"]["role"] = ur.carrier
    base_event["claims"]["id"] = 99
    base_event["body"] = '{"location": "12345"}'
    mock_shipment.status = ss.created
    mock_shipment.assigned_carrier_id = 99
    mock_session().__enter__().query().filter_by().first.return_value = mock_shipment
    response = handler(base_event, {})
    assert response["statusCode"] == HTTPStatus.FORBIDDEN
    assert "not in transit" in response["body"]
