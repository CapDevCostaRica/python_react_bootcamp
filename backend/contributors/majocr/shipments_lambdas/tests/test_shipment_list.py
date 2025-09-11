from app.common.python.common.database.models import ShipmentStatus
from tests.conftest import generate_token

# List Shipments

# 1. Successful listing of shipments with valid token and no status filter
def test_successful_list_shipments_with_valid_token(client, mocker):
    mock_row_1 = mocker.Mock()
    mock_row_1.id = 101
    mock_row_1.status = ShipmentStatus.in_transit
    mock_row_1.origin_warehouse_name = "Zarcero"
    mock_row_1.origin_warehouse_postal_code = "20102"
    mock_row_1.target_warehouse_name = "San José"
    mock_row_1.target_warehouse_postal_code = "10101"
    mock_row_1.carrier_username = "Carrier1"
    mock_row_1.in_transit_by_username = None
    mock_row_1.delivered_by_username = None
    mock_row_1.shipment_locations = []

    mock_row_2 = mocker.Mock()
    mock_row_2.id = 102
    mock_row_2.status = ShipmentStatus.created
    mock_row_2.origin_warehouse_name = "Zarcero"
    mock_row_2.origin_warehouse_postal_code = "20102"
    mock_row_2.target_warehouse_name = "San José"
    mock_row_2.target_warehouse_postal_code = "10101"
    mock_row_2.carrier_username = "Carrier1"
    mock_row_2.in_transit_by_username = "Carrier1"
    mock_row_2.delivered_by_username = None
    mock_row_2.shipment_locations = []

    mock_query = mocker.Mock()
    mock_query.select_from.return_value = mock_query
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_row_1, mock_row_2]

    mock_session = mocker.Mock()
    mock_session.query.return_value = mock_query

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.shipment_list.src.app.get_session", return_value=mock_context)

    token = generate_token(role="carrier", warehouse_id=42)

    response = client.post("/shipment/list", headers={"Authorization": token}, json={})
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, dict)
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 2
    assert all("id" in shipment and "status" in shipment for shipment in data["results"])
    
# 2. Successful listing of shipments with valid token and status filter
def test_successful_list_shipments_with_status_filter(client, mocker):
    mock_row = mocker.Mock()
    mock_row.id = 102
    mock_row.status = ShipmentStatus.in_transit
    mock_row.origin_warehouse_name = "Zarcero"
    mock_row.origin_warehouse_postal_code = "20102"
    mock_row.target_warehouse_name = "San José"
    mock_row.target_warehouse_postal_code = "10101"
    mock_row.carrier_username = "Carrier1"
    mock_row.in_transit_by_username = "Carrier1"
    mock_row.delivered_by_username = None
    mock_row.shipment_locations = []

    mock_query = mocker.Mock()
    mock_query.select_from.return_value = mock_query
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_row]

    mock_session = mocker.Mock()
    mock_session.query.return_value = mock_query

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.shipment_list.src.app.get_session", return_value=mock_context)

    token = generate_token(role="carrier", warehouse_id=42)

    response = client.post("/shipment/list", headers={"Authorization": token}, json={"status": "in_transit"})
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, dict)
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    assert data["results"][0]["status"] == ShipmentStatus.in_transit.value

# 3. Successful listing of shipments with valid token and date range filter
def test_successful_list_shipments_with_date_range_filter(client, mocker):
    mock_row = mocker.Mock()
    mock_row.id = 103
    mock_row.status = ShipmentStatus.created
    mock_row.origin_warehouse_name = "Zarcero"
    mock_row.origin_warehouse_postal_code = "20102"
    mock_row.target_warehouse_name = "San José"
    mock_row.target_warehouse_postal_code = "10101"
    mock_row.carrier_username = "Carrier1"
    mock_row.in_transit_by_username = None
    mock_row.delivered_by_username = None
    mock_row.shipment_locations = []

    from_date = "2025-09-01"
    to_date = "2025-09-10"

    mock_query = mocker.Mock()
    mock_query.select_from.return_value = mock_query
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_row]

    mock_session = mocker.Mock()
    mock_session.query.return_value = mock_query

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.shipment_list.src.app.get_session", return_value=mock_context)

    token = generate_token(role="carrier", warehouse_id=42)

    response = client.post(
        "/shipment/list",
        headers={"Authorization": token},
        json={"date": {"from_date": from_date, "to_date": to_date}}
    )
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, dict)
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == 103
    assert data["results"][0]["status"] == ShipmentStatus.created.value
    
# 4. Successful listing of shipments with valid token and carrier filter
def test_successful_list_shipments_with_carrier_filter(client, mocker):
    mock_row = mocker.Mock()
    mock_row.id = 104
    mock_row.status = ShipmentStatus.in_transit
    mock_row.origin_warehouse_name = "Zarcero"
    mock_row.origin_warehouse_postal_code = "20102"
    mock_row.target_warehouse_name = "San José"
    mock_row.target_warehouse_postal_code = "10101"
    mock_row.carrier_username = "Carrier7"
    mock_row.in_transit_by_username = "Carrier7"
    mock_row.delivered_by_username = None
    mock_row.shipment_locations = []

    mock_query = mocker.Mock()
    mock_query.select_from.return_value = mock_query
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_row]

    mock_session = mocker.Mock()
    mock_session.query.return_value = mock_query

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.shipment_list.src.app.get_session", return_value=mock_context)

    token = generate_token(role="carrier", warehouse_id=42)

    response = client.post(
        "/shipment/list",
        headers={"Authorization": token},
        json={"carrier": 7}
    )
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, dict)
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    assert data["results"][0]["carrier"]["username"] == "Carrier7"
    assert data["results"][0]["status"] == ShipmentStatus.in_transit.value
    
# 5. Successful listing of shipments with valid token and id filter
def test_successful_list_shipments_with_id_filter(client, mocker):
    mock_row = mocker.Mock()
    mock_row.id = 105
    mock_row.status = ShipmentStatus.delivered
    mock_row.origin_warehouse_name = "Zarcero"
    mock_row.origin_warehouse_postal_code = "20102"
    mock_row.target_warehouse_name = "San José"
    mock_row.target_warehouse_postal_code = "10101"
    mock_row.carrier_username = "Carrier5"
    mock_row.delivered_by_username = "Carrier5"
    mock_row.in_transit_by_username = "Carrier5"
    mock_row.shipment_locations = []

    mock_query = mocker.Mock()
    mock_query.select_from.return_value = mock_query
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_row]

    mock_session = mocker.Mock()
    mock_session.query.return_value = mock_query

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.shipment_list.src.app.get_session", return_value=mock_context)

    token = generate_token(role="carrier", warehouse_id=42)

    response = client.post(
        "/shipment/list",
        headers={"Authorization": token},
        json={"id": 105}
    )
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, dict)
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == 105
    assert data["results"][0]["status"] == ShipmentStatus.delivered

# 6. Successful listing of shipments with valid token and multiple filters
def test_successful_list_shipments_with_multiple_filters(client, mocker):
    mock_row = mocker.Mock()
    mock_row.id = 106
    mock_row.status = ShipmentStatus.in_transit
    mock_row.origin_warehouse_name = "Zarcero"
    mock_row.origin_warehouse_postal_code = "20102"
    mock_row.target_warehouse_name = "San José"
    mock_row.target_warehouse_postal_code = "10101"
    mock_row.carrier_username = "Carrier7"
    mock_row.in_transit_by_username = "Carrier7"
    mock_row.delivered_by_username = None
    mock_row.shipment_locations = []

    mock_query = mocker.Mock()
    mock_query.select_from.return_value = mock_query
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_row]

    mock_session = mocker.Mock()
    mock_session.query.return_value = mock_query

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.shipment_list.src.app.get_session", return_value=mock_context)

    token = generate_token(role="carrier", warehouse_id=42)

    filters = {
        "status": "in_transit",
        "carrier": 7,
        "date": {
            "from_date": "2025-09-01",
            "to_date": "2025-09-10"
        }
    }

    response = client.post("/shipment/list", headers={"Authorization": token}, json=filters)
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, dict)
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == 106
    assert data["results"][0]["status"] == ShipmentStatus.in_transit.value
    assert data["results"][0]["carrier"]["username"] == "Carrier7"
    
# 7. A Global Manager can view all shipments across the state
def test_global_manager_can_view_all_shipments(client, mocker):
    mock_row_1 = mocker.Mock()
    mock_row_1.id = 201
    mock_row_1.status = ShipmentStatus.created
    mock_row_1.origin_warehouse_name = "Heredia"
    mock_row_1.origin_warehouse_postal_code = "40101"
    mock_row_1.target_warehouse_name = "Cartago"
    mock_row_1.target_warehouse_postal_code = "30101"
    mock_row_1.carrier_username = "CarrierA"
    mock_row_1.in_transit_by_username = None
    mock_row_1.delivered_by_username = None
    mock_row_1.shipment_locations = []

    mock_row_2 = mocker.Mock()
    mock_row_2.id = 202
    mock_row_2.status = ShipmentStatus.delivered
    mock_row_2.origin_warehouse_name = "Alajuela"
    mock_row_2.origin_warehouse_postal_code = "20101"
    mock_row_2.target_warehouse_name = "Puntarenas"
    mock_row_2.target_warehouse_postal_code = "60101"
    mock_row_2.carrier_username = "CarrierB"
    mock_row_2.in_transit_by_username = "CarrierB"
    mock_row_2.delivered_by_username = "CarrierB"
    mock_row_2.shipment_locations = []

    mock_query = mocker.Mock()
    mock_query.select_from.return_value = mock_query
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_row_1, mock_row_2]

    mock_session = mocker.Mock()
    mock_session.query.return_value = mock_query

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.shipment_list.src.app.get_session", return_value=mock_context)

    token = generate_token(role="global_manager")

    response = client.post("/shipment/list", headers={"Authorization": token}, json={})
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, dict)
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 2
    assert {shipment["id"] for shipment in data["results"]} == {201, 202}
    
# 8. A Store Manager can view shipments where their store is either the origin or destination
def test_store_manager_can_view_store_related_shipments(client, mocker):
    mock_row_1 = mocker.Mock()
    mock_row_1.id = 301
    mock_row_1.status = ShipmentStatus.created
    mock_row_1.origin_warehouse_name = "Puntarenas"
    mock_row_1.origin_warehouse_postal_code = "50101"
    mock_row_1.target_warehouse_name = "San José"
    mock_row_1.target_warehouse_postal_code = "10101"
    mock_row_1.carrier_username = "CarrierX"
    mock_row_1.in_transit_by_username = None
    mock_row_1.delivered_by_username = None
    mock_row_1.shipment_locations = []

    mock_row_2 = mocker.Mock()
    mock_row_2.id = 302
    mock_row_2.status = ShipmentStatus.in_transit
    mock_row_2.origin_warehouse_name = "Cartago"
    mock_row_2.origin_warehouse_postal_code = "30102"
    mock_row_2.target_warehouse_name = "Puntarenas"
    mock_row_2.target_warehouse_postal_code = "50101"
    mock_row_2.carrier_username = "CarrierY"
    mock_row_2.in_transit_by_username = "CarrierY"
    mock_row_2.delivered_by_username = None
    mock_row_2.shipment_locations = []

    mock_query = mocker.Mock()
    mock_query.select_from.return_value = mock_query
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_row_1, mock_row_2]

    mock_session = mocker.Mock()
    mock_session.query.return_value = mock_query

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.shipment_list.src.app.get_session", return_value=mock_context)

    token = generate_token(role="store_manager", store_id=88)

    response = client.post("/shipment/list", headers={"Authorization": token}, json={})
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, dict)
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 2
    assert {shipment["id"] for shipment in data["results"]} == {301, 302}
    
# 9. A Warehouse Staff can view shipments where their warehouse is either the origin or destinations
def test_warehouse_staff_can_view_warehouse_related_shipments(client, mocker):
    mock_row_1 = mocker.Mock()
    mock_row_1.id = 401
    mock_row_1.status = ShipmentStatus.created
    mock_row_1.origin_warehouse_name = "Alajuela"
    mock_row_1.origin_warehouse_postal_code = "20102"
    mock_row_1.target_warehouse_name = "Warehouse 42"
    mock_row_1.target_warehouse_postal_code = "50101"
    mock_row_1.carrier_username = "CarrierZ"
    mock_row_1.in_transit_by_username = None
    mock_row_1.delivered_by_username = None
    mock_row_1.shipment_locations = []

    mock_row_2 = mocker.Mock()
    mock_row_2.id = 402
    mock_row_2.status = ShipmentStatus.in_transit
    mock_row_2.origin_warehouse_name = "Warehouse 42"
    mock_row_2.origin_warehouse_postal_code = "50101"
    mock_row_2.target_warehouse_name = "San José"
    mock_row_2.target_warehouse_postal_code = "10101"
    mock_row_2.carrier_username = "CarrierZ"
    mock_row_2.in_transit_by_username = "CarrierZ"
    mock_row_2.delivered_by_username = None
    mock_row_2.shipment_locations = []

    mock_query = mocker.Mock()
    mock_query.select_from.return_value = mock_query
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_row_1, mock_row_2]

    mock_session = mocker.Mock()
    mock_session.query.return_value = mock_query

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.shipment_list.src.app.get_session", return_value=mock_context)

    token = generate_token(role="warehouse_staff", warehouse_id=42)

    response = client.post("/shipment/list", headers={"Authorization": token}, json={})
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, dict)
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 2
    assert {shipment["id"] for shipment in data["results"]} == {401, 402}
    
# 10. A Carrier can view shipments assigned to them
def test_carrier_can_view_assigned_shipments(client, mocker):
    mock_row_1 = mocker.Mock()
    mock_row_1.id = 501
    mock_row_1.status = ShipmentStatus.in_transit
    mock_row_1.origin_warehouse_name = "Zarcero"
    mock_row_1.origin_warehouse_postal_code = "20102"
    mock_row_1.target_warehouse_name = "San José"
    mock_row_1.target_warehouse_postal_code = "10101"
    mock_row_1.carrier_username = "Carrier77"
    mock_row_1.in_transit_by_username = "Carrier77"
    mock_row_1.delivered_by_username = None
    mock_row_1.shipment_locations = []

    mock_row_2 = mocker.Mock()
    mock_row_2.id = 502
    mock_row_2.status = ShipmentStatus.delivered
    mock_row_2.origin_warehouse_name = "Alajuela"
    mock_row_2.origin_warehouse_postal_code = "20103"
    mock_row_2.target_warehouse_name = "Cartago"
    mock_row_2.target_warehouse_postal_code = "30103"
    mock_row_2.carrier_username = "Carrier77"
    mock_row_2.in_transit_by_username = "Carrier77"
    mock_row_2.delivered_by_username = "Carrier77"
    mock_row_2.shipment_locations = []

    mock_query = mocker.Mock()
    mock_query.select_from.return_value = mock_query
    mock_query.outerjoin.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [mock_row_1, mock_row_2]

    mock_session = mocker.Mock()
    mock_session.query.return_value = mock_query

    mock_context = mocker.MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None

    mocker.patch("app.functions.shipment_list.src.app.get_session", return_value=mock_context)

    token = generate_token(role="carrier", sub=77)

    response = client.post("/shipment/list", headers={"Authorization": token}, json={})
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, dict)
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 2
    assert {shipment["id"] for shipment in data["results"]} == {501, 502}
    assert all(shipment["carrier"]["username"] == "Carrier77" for shipment in data["results"])
    
# 11. Failed listing of shipments with invalid token
def test_failed_list_shipments_with_invalid_token(client):
    invalid_token = "Bearer this.is.not.a.valid.token"

    response = client.post("/shipment/list", headers={"Authorization": invalid_token}, json={})
    assert response.status_code == 401

    data = response.get_json()
    assert isinstance(data, dict)
    assert "error" in data
    assert "token" in data["error"].lower() or "authorization" in data["error"].lower()

# 12. Failed listing of shipments with missing token
def test_failed_list_shipments_with_missing_token(client):
    response = client.post("/shipment/list", json={})
    assert response.status_code == 401

    data = response.get_json()
    assert isinstance(data, dict)
    assert "error" in data
    assert "unauthorized" in data["error"].lower()
    
# 13. Failed listing of shipments with unauthorized role
def test_failed_list_shipments_with_unauthorized_role(client):
    token = generate_token(role="guest")

    response = client.post("/shipment/list", headers={"Authorization": token}, json={})
    assert response.status_code == 403

    data = response.get_json()
    assert isinstance(data, dict)
    assert "error" in data
    assert "forbidden" in data["error"].lower() or "unauthorized" in data["error"].lower()