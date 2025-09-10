from datetime import datetime
from tests.conftest import generate_token

# Update Shipment

# 1. I can update the status of a shipment to "In Transit" when it is "Created" and the dates are set correctly
def test_update_shipment_status_to_in_transit_when_created(client, mocker):
    mock_shipment = mocker.Mock()
    mock_shipment.id = 601
    mock_shipment.status = "created"
    mock_shipment.in_transit_at = None
    mock_shipment.in_transit_by_id = None
    mock_shipment.delivered_at = None
    mock_shipment.delivered_by_id = None

    mock_query = mocker.Mock()
    mock_query.filter_by.return_value.first.return_value = mock_shipment

    mock_session = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_session.query.return_value.get.return_value = mock_shipment
    mock_session.commit.return_value = None

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.update_shipment.src.app.get_session", return_value=mock_context)

    token = generate_token(role="carrier", sub=77)

    payload = {
        "status": "in_transit",
    }

    print("Mocked shipment status:", mock_shipment.status)
    response = client.post("/shipment/601", headers={"Authorization": token}, json=payload)

    assert response.status_code == 200, f"Expected 200, got {response.status_code} with body: {response.get_json()}"
    data = response.get_json()
    assert isinstance(data, dict)
    assert "updated" in data["message"].lower()
    assert "in_transit" in data["message"].lower()
    assert mock_shipment.status == "in_transit"
    assert mock_shipment.in_transit_by_id == 77
    assert mock_shipment.in_transit_at is not None

    
# 2. I can update the status of a shipment to "Delivered" when it is "In Transit" and the dates are set correctly
from datetime import datetime
from tests.conftest import generate_token

def test_update_shipment_status_to_delivered_when_in_transit(client, mocker):
    mock_shipment = mocker.Mock()
    mock_shipment.id = 602
    mock_shipment.status = "in_transit"
    mock_shipment.in_transit_at = datetime.utcnow()
    mock_shipment.in_transit_by_id = 77
    mock_shipment.delivered_at = None
    mock_shipment.delivered_by_id = None

    mock_query = mocker.Mock()
    mock_query.filter_by.return_value.first.return_value = mock_shipment

    mock_session = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_session.query.return_value.get.return_value = mock_shipment
    mock_session.commit.return_value = None

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.update_shipment.src.app.get_session", return_value=mock_context)

    token = generate_token(role="warehouse_staff", sub=88)

    payload = {
        "status": "delivered"
    }

    response = client.post("/shipment/602", headers={"Authorization": token}, json=payload)

    assert response.status_code == 200, f"Expected 200, got {response.status_code} with body: {response.get_json()}"
    data = response.get_json()
    assert isinstance(data, dict)
    assert "delivered" in data["message"].lower()

    assert mock_shipment.status == "delivered"
    assert mock_shipment.delivered_by_id == 88
    assert mock_shipment.delivered_at is not None
    
# 3. I cannot update the status of a shipment to "In Transit" when it is already "In Transit"
def test_cannot_update_status_to_in_transit_when_already_in_transit(client, mocker):
    mock_shipment = mocker.Mock()
    mock_shipment.id = 603
    mock_shipment.status = "in_transit"
    mock_shipment.in_transit_at = datetime.utcnow()
    mock_shipment.in_transit_by_id = 77
    mock_shipment.delivered_at = None
    mock_shipment.delivered_by_id = None

    mock_query = mocker.Mock()
    mock_query.filter_by.return_value.first.return_value = mock_shipment

    mock_session = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_session.query.return_value.get.return_value = mock_shipment
    mock_session.commit.return_value = None

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.update_shipment.src.app.get_session", return_value=mock_context)

    token = generate_token(role="carrier", sub=77)

    payload = {
        "status": "in_transit"
    }

    response = client.post("/shipment/603", headers={"Authorization": token}, json=payload)

    assert response.status_code == 400, f"Expected 400, got {response.status_code} with body: {response.get_json()}"
    data = response.get_json()
    assert "status" in data["error"]
    assert "Shipment is already in 'in_transit'" in data["error"]["status"][0]
    
# 4. I cannot update the status of a shipment to "Delivered" when it is already "Delivered"
def test_cannot_update_status_to_delivered_when_already_delivered(client, mocker):
    mock_shipment = mocker.Mock()
    mock_shipment.id = 604
    mock_shipment.status = "delivered"
    mock_shipment.in_transit_at = datetime.utcnow()
    mock_shipment.in_transit_by_id = 77
    mock_shipment.delivered_at = datetime.utcnow()
    mock_shipment.delivered_by_id = 88

    mock_query = mocker.Mock()
    mock_query.filter_by.return_value.first.return_value = mock_shipment

    mock_session = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_session.query.return_value.get.return_value = mock_shipment
    mock_session.commit.return_value = None

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.update_shipment.src.app.get_session", return_value=mock_context)

    token = generate_token(role="warehouse_staff", sub=88)

    payload = {
        "status": "delivered"
    }

    response = client.post("/shipment/604", headers={"Authorization": token}, json=payload)

    assert response.status_code == 400, f"Expected 400, got {response.status_code} with body: {response.get_json()}"
    data = response.get_json()
    assert "status" in data["error"]
    assert "Shipment must be 'in_transit' to mark as 'delivered'" in data["error"]["status"][0]
    
# 5. I cannot update the status of a shipment to "Delivered" when it is "Created"
def test_cannot_update_status_to_delivered_when_created(client, mocker):
    mock_shipment = mocker.Mock()
    mock_shipment.id = 605
    mock_shipment.status = "created"
    mock_shipment.in_transit_at = None
    mock_shipment.in_transit_by_id = None
    mock_shipment.delivered_at = None
    mock_shipment.delivered_by_id = None

    mock_query = mocker.Mock()
    mock_query.filter_by.return_value.first.return_value = mock_shipment

    mock_session = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_session.query.return_value.get.return_value = mock_shipment
    mock_session.commit.return_value = None

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.update_shipment.src.app.get_session", return_value=mock_context)

    token = generate_token(role="warehouse_staff", sub=88)

    payload = {
        "status": "delivered"
    }

    response = client.post("/shipment/605", headers={"Authorization": token}, json=payload)

    assert response.status_code == 400, f"Expected 400, got {response.status_code} with body: {response.get_json()}"
    data = response.get_json()
    assert "status" in data["error"]
    assert "Shipment must be 'in_transit' to mark as 'delivered'" in data["error"]["status"][0]

# 6. I can update the location of a shipment when it is "In Transit" and I am the assigned carrier
def test_can_update_location_when_in_transit_and_assigned_carrier(client, mocker):
    mock_shipment = mocker.Mock()
    mock_shipment.id = 606
    mock_shipment.status = "in_transit"
    mock_shipment.in_transit_at = datetime.utcnow()
    mock_shipment.in_transit_by_id = 77
    mock_shipment.delivered_at = None
    mock_shipment.delivered_by_id = None
    mock_shipment.assigned_carrier_id = 77

    mock_query = mocker.Mock()
    mock_query.filter_by.return_value.first.return_value = mock_shipment

    mock_session = mocker.Mock()
    mock_session.query.return_value = mock_query
    mock_session.query.return_value.get.return_value = mock_shipment
    mock_session.commit.return_value = None

    mock_location = mocker.Mock()
    mocker.patch("app.functions.update_shipment.src.app.models.ShipmentLocation", return_value=mock_location)

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.update_shipment.src.app.get_session", return_value=mock_context)

    token = generate_token(role="carrier", sub=77)

    payload = {
        "status": "in_transit",
        "location": "50601"
    }

    response = client.post("/shipment/606", headers={"Authorization": token}, json=payload)

    assert response.status_code == 200, f"Expected 200, got {response.status_code} with body: {response.get_json()}"
    data = response.get_json()
    assert "location" in data["message"].lower()
    assert "registered" in data["message"].lower()

    mock_session.add.assert_called_once_with(mock_location)