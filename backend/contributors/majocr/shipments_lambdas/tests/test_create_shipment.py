from datetime import datetime
from tests.conftest import generate_token

# Create Shipment

# 1. I can create a shipment with valid data as a Warehouse Staff or Store Manager, only if the origin and destination warehouses are different and the origin warehouse matches my assigned warehouse
def test_can_create_shipment_with_valid_data_as_warehouse_staff(client, mocker):
    mock_carrier = mocker.Mock()
    mock_carrier.id = 99
    mock_carrier.role = "carrier"

    payload = {
        "origin_warehouse_id": 101,
        "destination_warehouse_id": 202,
        "assigned_carrier_id": 99
    }

    mock_user = mocker.Mock()
    mock_user.id = 88
    mock_user.role = "warehouse_staff"
    mock_user.assigned_warehouse_id = 101

    mock_shipment = mocker.Mock()
    mock_shipment.id = 1
    mock_shipment.origin_warehouse_id = 101
    mock_shipment.destination_warehouse_id = 202
    mock_shipment.assigned_carrier_id = None
    mock_shipment.status = "created"
    mock_shipment.created_by_id = 88

    mocker.patch("app.functions.create_shipement.src.app.models.Shipment", return_value=mock_shipment)

    mock_session = mocker.Mock()
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.query.return_value.get.return_value = mock_user
    mock_session.query.return_value.get.side_effect = lambda id: mock_carrier if id == 99 else mock_user
    
    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.create_shipement.src.app.get_session", return_value=mock_context)

    token = generate_token(role="warehouse_staff", sub=88)

    response = client.post("/shipment/", headers={"Authorization": token}, json=payload)

    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Shipment created successfully."
    
# 2. I cannot create a shipment with the same origin and destination warehouses
def test_cannot_create_shipment_with_same_origin_and_destination(client, mocker):
    mock_carrier = mocker.Mock()
    mock_carrier.id = 99
    mock_carrier.role = "carrier"

    payload = {
        "origin_warehouse_id": 101,
        "destination_warehouse_id": 101,
        "assigned_carrier_id": 99
    }

    mock_user = mocker.Mock()
    mock_user.id = 88
    mock_user.role = "warehouse_staff"
    mock_user.assigned_warehouse_id = 101

    mock_session = mocker.Mock()
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.query.return_value.get.return_value = mock_user

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.create_shipement.src.app.get_session", return_value=mock_context)

    token = generate_token(role="warehouse_staff", sub=88)

    response = client.post("/shipment/", headers={"Authorization": token}, json=payload)

    assert response.status_code == 400, f"Expected 400, got {response.status_code} with body: {response.get_json()}"
    data = response.get_json()
    assert "destination_warehouse_id" in data["error"]
    assert "Origin and destination must be different." in data["error"]["destination_warehouse_id"][0]
    
# 3. I cannot create a shipment with missing required fields
def test_cannot_create_shipment_with_missing_required_fields(client, mocker):
    payload = {
        "destination_warehouse_id": 202
    }

    mock_user = mocker.Mock()
    mock_user.id = 88
    mock_user.role = "warehouse_staff"
    mock_user.assigned_warehouse_id = 101

    mock_session = mocker.Mock()
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.query.return_value.get.return_value = mock_user

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.create_shipement.src.app.get_session", return_value=mock_context)

    token = generate_token(role="warehouse_staff", sub=88)

    response = client.post("/shipment/", headers={"Authorization": token}, json=payload)

    assert response.status_code == 400, f"Expected 400, got {response.status_code} with body: {response.get_json()}"
    data = response.get_json()
    assert "origin_warehouse_id" in data["error"]
    assert "Missing data for required field." in data["error"]["origin_warehouse_id"][0]

    assert "assigned_carrier_id" in data["error"]
    assert "Missing data for required field." in data["error"]["assigned_carrier_id"][0]
    
# 4. I cannot create a shipment with invalid warehouse IDs
def test_cannot_create_shipment_with_invalid_warehouse_ids(client, mocker):
    mock_carrier = mocker.Mock()
    mock_carrier.id = 99
    mock_carrier.role = "carrier"

    payload = {
        "origin_warehouse_id": 9999,
        "destination_warehouse_id": 8888,
        "assigned_carrier_id": 99
    }

    mock_user = mocker.Mock()
    mock_user.id = 88
    mock_user.role = "warehouse_staff"
    mock_user.assigned_warehouse_id = 101

    mock_session = mocker.Mock()
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.query.return_value.get.side_effect = lambda id: {
        99: mock_carrier,
        88: mock_user
    }.get(id, None)

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.create_shipement.src.app.get_session", return_value=mock_context)
    
    token = generate_token(role="warehouse_staff", sub=88)

    response = client.post("/shipment/", headers={"Authorization": token}, json=payload)

    assert response.status_code == 400, f"Expected 400, got {response.status_code} with body: {response.get_json()}"
    data = response.get_json()
    assert "origin_warehouse_id" in data["error"] or "destination_warehouse_id" in data["error"]
    assert any("invalid" in msg.lower() or "not found" in msg.lower() for msgs in data["error"].values() for msg in msgs)
    
# 5. I cannot create a shipment if my warehouse does not match the origin warehouse
def test_cannot_create_shipment_if_origin_does_not_match_assigned_warehouse(client, mocker):
    mock_carrier = mocker.Mock()
    mock_carrier.id = 99
    mock_carrier.role = "carrier"

    mock_origin = mocker.Mock()
    mock_origin.id = 999
    
    mock_destination = mocker.Mock()
    mock_destination.id = 202

    payload = {
        "origin_warehouse_id": 999,
        "destination_warehouse_id": 202,
        "assigned_carrier_id": 99
    }

    mock_user = mocker.Mock()
    mock_user.id = 88
    mock_user.role = "warehouse_staff"
    mock_user.assigned_warehouse_id = 101

    mock_session = mocker.Mock()
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.query.return_value.get.side_effect = lambda id: {
        99: mock_carrier,
        88: mock_user,
        999: mock_origin,
        202: mock_destination
    }.get(id, None)

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.create_shipement.src.app.get_session", return_value=mock_context)

    token = generate_token(role="warehouse_staff", sub=88, warehouse_id=101)

    response = client.post("/shipment/", headers={"Authorization": token}, json=payload)

    assert response.status_code == 400, f"Expected 400, got {response.status_code} with body: {response.get_json()}"
    data = response.get_json()
    assert "origin_warehouse_id" in data["error"]
    assert "You are only authorized to create shipments from your assigned warehouse." in data["error"]["origin_warehouse_id"][0]