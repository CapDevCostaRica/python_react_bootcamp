#!/usr/bin/env python3
import os
import sys
import pytest
import requests
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = os.environ.get("API_URL", "http://localhost:4000")


class TestShipmentsAPI:
    
    @pytest.fixture(scope="class")
    def auth_tokens(self):
        tokens = {}
        
        test_users = [
            "GlobalManager",
            "ManagerAtSan Francisco Warehouse", 
            "StaffAtSan Francisco Warehouse",
            "StaffAtLos Angeles Warehouse",
            "Carrier1",
            "Carrier2"
        ]
        
        for username in test_users:
            login_data = {"username": username}
            response = requests.post(f"{BASE_URL}/login", json=login_data)
            if response.status_code == 200:
                tokens[username] = response.json().get("access_token")
            else:
                pytest.fail(f"Failed to login user {username}: {response.status_code} - {response.text}")
        
        return tokens
    
    @pytest.fixture(scope="class")
    def carrier_ids(self, auth_tokens):
        import base64
        import json
        
        carrier_ids = []
        
        for username in ["Carrier1", "Carrier2"]:
            if username in auth_tokens:
                token = auth_tokens[username]
                try:
                    payload = token.split('.')[1]
                    payload += '=' * (4 - len(payload) % 4)
                    decoded = base64.b64decode(payload)
                    user_data = json.loads(decoded)
                    carrier_ids.append(int(user_data['sub']))
                except Exception as e:
                    print(f"Failed to decode token for {username}: {e}")
        
        if not carrier_ids:
            sf_staff_token = auth_tokens["StaffAtSan Francisco Warehouse"]
            sf_headers = {"Authorization": f"Bearer {sf_staff_token}"}
            
            for carrier_id in [5, 6, 7, 8]:
                shipment_data = {
                    "origin_warehouse_id": 1,
                    "destination_warehouse_id": 2,
                    "assigned_carrier_id": carrier_id
                }
                
                response = requests.post(f"{BASE_URL}/shipment/", json=shipment_data, headers=sf_headers)
                if response.status_code == 201:
                    carrier_ids.append(carrier_id)
                    break
        
        assert carrier_ids, "Could not find any valid carrier IDs"
        return carrier_ids
    
    @pytest.fixture(scope="class")
    def test_shipment_id(self, auth_tokens, carrier_ids):
        token = auth_tokens["StaffAtSan Francisco Warehouse"]
        headers = {"Authorization": f"Bearer {token}"}
        
        shipment_data = {
            "origin_warehouse_id": 1,
            "destination_warehouse_id": 2,
            "assigned_carrier_id": carrier_ids[0]
        }
        
        response = requests.post(f"{BASE_URL}/shipment/", json=shipment_data, headers=headers)
        assert response.status_code == 201, f"Failed to create test shipment: {response.text}"
        
        shipment = response.json()
        return shipment["id"]


class TestLogin(TestShipmentsAPI):
    
    @pytest.mark.parametrize("username,expected_status", [
        ("GlobalManager", 200),
        ("ManagerAtSan Francisco Warehouse", 200),
        ("StaffAtSan Francisco Warehouse", 200),
        ("Carrier1", 200),
        ("InvalidUser", 404),
        ("", 404),
    ])
    def test_login(self, username, expected_status):
        login_data = {"username": username}
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        
        assert response.status_code == expected_status
        
        if expected_status == 200:
            data = response.json()
            assert "access_token" in data
            assert "token_type" in data
            assert data["token_type"] == "bearer"
    
    def test_login_missing_username(self):
        response = requests.post(f"{BASE_URL}/login", json={})
        assert response.status_code == 400


class TestShipmentList(TestShipmentsAPI):
    
    @pytest.mark.parametrize("username,expected_shipments", [
        ("GlobalManager", "all"),
        ("ManagerAtSan Francisco Warehouse", "warehouse_related"),
        ("StaffAtSan Francisco Warehouse", "warehouse_related"),
        ("Carrier1", "assigned_only"),
    ])
    def test_list_shipments_by_role(self, auth_tokens, username, expected_shipments):
        token = auth_tokens[username]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(f"{BASE_URL}/shipment/list", json={}, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert "result_count" in data
        
        assert isinstance(data["results"], list)
        assert data["result_count"] >= 0
    
    @pytest.mark.parametrize("filters", [
        {"status": "created"},
        {"status": "in_transit"},
        {"status": "delivered"},
        {"id": 1},
        {"carrier": "dynamic"},
        {"date": {"from_date": "2024-01-01T00:00:00", "to_date": "2024-12-31T23:59:59"}},
        {"status": "created", "carrier": "dynamic"},
        {"status": "in_transit", "date": {"from_date": "2024-01-01T00:00:00"}},
    ])
    def test_list_shipments_with_filters(self, auth_tokens, carrier_ids, filters):
        token = auth_tokens["GlobalManager"]
        headers = {"Authorization": f"Bearer {token}"}
        
        if filters.get("carrier") == "dynamic":
            filters = filters.copy()
            filters["carrier"] = carrier_ids[0]
        
        response = requests.post(f"{BASE_URL}/shipment/list", json=filters, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert "result_count" in data
    
    def test_list_shipments_unauthorized(self):
        response = requests.post(f"{BASE_URL}/shipment/list", json={})
        assert response.status_code == 401
    
    def test_list_shipments_invalid_token(self):
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.post(f"{BASE_URL}/shipment/list", json={}, headers=headers)
        assert response.status_code == 401


class TestCreateShipment(TestShipmentsAPI):
    
    @pytest.mark.parametrize("username,shipment_data,expected_status", [
        ("StaffAtSan Francisco Warehouse", {
            "origin_warehouse_id": 1,
            "destination_warehouse_id": 2,
            "assigned_carrier_id": "dynamic"
        }, 201),
        ("StaffAtLos Angeles Warehouse", {
            "origin_warehouse_id": 2,
            "destination_warehouse_id": 3,
            "assigned_carrier_id": "dynamic"
        }, 201),
        ("StaffAtSan Francisco Warehouse", {
            "origin_warehouse_id": 1,
            "destination_warehouse_id": 1,
            "assigned_carrier_id": "dynamic"
        }, 400),
        ("StaffAtSan Francisco Warehouse", {
            "origin_warehouse_id": 2,
            "destination_warehouse_id": 3,
            "assigned_carrier_id": "dynamic"
        }, 400),
    ])
    def test_create_shipment(self, auth_tokens, carrier_ids, username, shipment_data, expected_status):
        token = auth_tokens[username]
        headers = {"Authorization": f"Bearer {token}"}
        
        if shipment_data.get("assigned_carrier_id") == "dynamic":
            shipment_data = shipment_data.copy()
            shipment_data["assigned_carrier_id"] = carrier_ids[0]
        
        response = requests.post(f"{BASE_URL}/shipment/", json=shipment_data, headers=headers)
        assert response.status_code == expected_status
        
        if expected_status == 201:
            data = response.json()
            assert "id" in data
            assert "status" in data
            assert data["status"] == "created"
            assert "created_at" in data
    
    def test_create_shipment_unauthorized_roles(self, auth_tokens, carrier_ids):
        unauthorized_users = [
            "GlobalManager",
            "ManagerAtSan Francisco Warehouse", 
            "Carrier1"
        ]
        
        shipment_data = {
            "origin_warehouse_id": 1,
            "destination_warehouse_id": 2,
            "assigned_carrier_id": carrier_ids[0]
        }
        
        for username in unauthorized_users:
            token = auth_tokens[username]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.post(f"{BASE_URL}/shipment/", json=shipment_data, headers=headers)
            assert response.status_code == 403, f"User {username} should not be able to create shipments"
    
    def test_create_shipment_missing_fields(self, auth_tokens, carrier_ids):
        token = auth_tokens["StaffAtSan Francisco Warehouse"]
        headers = {"Authorization": f"Bearer {token}"}
        
        shipment_data = {
            "origin_warehouse_id": 1,
            "assigned_carrier_id": carrier_ids[0]
        }
        
        response = requests.post(f"{BASE_URL}/shipment/", json=shipment_data, headers=headers)
        assert response.status_code == 400
    
    def test_create_shipment_unauthorized(self, carrier_ids):
        shipment_data = {
            "origin_warehouse_id": 1,
            "destination_warehouse_id": 2,
            "assigned_carrier_id": carrier_ids[0]
        }
        
        response = requests.post(f"{BASE_URL}/shipment/", json=shipment_data)
        assert response.status_code == 401


class TestUpdateShipment(TestShipmentsAPI):
    
    @pytest.mark.parametrize("username,shipment_id,update_data,expected_status", [
        ("StaffAtSan Francisco Warehouse", 1, {"status": "in_transit"}, 200),
        ("StaffAtSan Francisco Warehouse", 1, {"status": "delivered"}, 200),
    ])
    def test_update_shipment_valid(self, auth_tokens, test_shipment_id, username, shipment_id, update_data, expected_status):
        actual_shipment_id = test_shipment_id if shipment_id == 1 else shipment_id
        
        token = auth_tokens[username]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(f"{BASE_URL}/shipment/{actual_shipment_id}", json=update_data, headers=headers)
        assert response.status_code == expected_status
        
        if expected_status == 200:
            data = response.json()
            assert "id" in data
            assert "status" in data
    
    @pytest.mark.parametrize("username,shipment_id,update_data,expected_status", [
        ("Carrier1", 1, {"status": "in_transit"}, 400),
        ("StaffAtSan Francisco Warehouse", 1, {"location": "90210"}, 400),
        ("Carrier2", 1, {"location": "90210"}, 403),
    ])
    def test_update_shipment_invalid_permissions(self, auth_tokens, test_shipment_id, username, shipment_id, update_data, expected_status):
        actual_shipment_id = test_shipment_id if shipment_id == 1 else shipment_id
        
        token = auth_tokens[username]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(f"{BASE_URL}/shipment/{actual_shipment_id}", json=update_data, headers=headers)
        assert response.status_code == expected_status
    
    @pytest.mark.parametrize("update_data", [
        {"status": "delivered"},
        {"status": "created"},
        {"location": "90210"},
    ])
    def test_update_shipment_invalid_transitions(self, auth_tokens, test_shipment_id, update_data):
        token = auth_tokens["StaffAtSan Francisco Warehouse"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(f"{BASE_URL}/shipment/{test_shipment_id}", json=update_data, headers=headers)
        assert response.status_code == 400
    
    def test_update_shipment_not_found(self, auth_tokens):
        token = auth_tokens["StaffAtSan Francisco Warehouse"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(f"{BASE_URL}/shipment/99999", json={"status": "in_transit"}, headers=headers)
        assert response.status_code == 404
    
    def test_update_shipment_missing_data(self, auth_tokens, test_shipment_id):
        token = auth_tokens["StaffAtSan Francisco Warehouse"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(f"{BASE_URL}/shipment/{test_shipment_id}", json={}, headers=headers)
        assert response.status_code == 400
    
    def test_update_shipment_unauthorized(self, test_shipment_id):
        response = requests.post(f"{BASE_URL}/shipment/{test_shipment_id}", json={"status": "in_transit"})
        assert response.status_code == 401


class TestIntegrationScenarios(TestShipmentsAPI):
    
    def test_complete_shipment_workflow(self, auth_tokens, carrier_ids):
        token = auth_tokens["StaffAtSan Francisco Warehouse"]
        headers = {"Authorization": f"Bearer {token}"}
        
        shipment_data = {
            "origin_warehouse_id": 1,
            "destination_warehouse_id": 2,
            "assigned_carrier_id": carrier_ids[0]
        }
        
        response = requests.post(f"{BASE_URL}/shipment/", json=shipment_data, headers=headers)
        assert response.status_code == 201
        shipment = response.json()
        shipment_id = shipment["id"]
        
        response = requests.post(f"{BASE_URL}/shipment/{shipment_id}", json={"status": "in_transit"}, headers=headers)
        assert response.status_code == 200
        
        carrier_token = auth_tokens["Carrier1"]
        carrier_headers = {"Authorization": f"Bearer {carrier_token}"}
        
        response = requests.post(f"{BASE_URL}/shipment/{shipment_id}", json={"location": "90210"}, headers=carrier_headers)
        assert response.status_code == 200
        
        response = requests.post(f"{BASE_URL}/shipment/{shipment_id}", json={"status": "delivered"}, headers=headers)
        assert response.status_code == 200
    
    def test_carrier_location_tracking(self, auth_tokens, test_shipment_id):
        staff_token = auth_tokens["StaffAtSan Francisco Warehouse"]
        staff_headers = {"Authorization": f"Bearer {staff_token}"}
        
        response = requests.post(f"{BASE_URL}/shipment/{test_shipment_id}", json={"status": "in_transit"}, headers=staff_headers)
        assert response.status_code == 200
        
        carrier_token = auth_tokens["Carrier1"]
        carrier_headers = {"Authorization": f"Bearer {carrier_token}"}
        
        locations = ["90210", "10001", "33101"]
        for location in locations:
            response = requests.post(f"{BASE_URL}/shipment/{test_shipment_id}", json={"location": location}, headers=carrier_headers)
            assert response.status_code == 200
    
    def test_role_based_shipment_visibility(self, auth_tokens, carrier_ids):
        sf_staff_token = auth_tokens["StaffAtSan Francisco Warehouse"]
        sf_staff_headers = {"Authorization": f"Bearer {sf_staff_token}"}
        
        shipment_data = {
            "origin_warehouse_id": 1,
            "destination_warehouse_id": 2,
            "assigned_carrier_id": carrier_ids[0]
        }
        
        response = requests.post(f"{BASE_URL}/shipment/", json=shipment_data, headers=sf_staff_headers)
        assert response.status_code == 201
        shipment_id = response.json()["id"]
        
        response = requests.post(f"{BASE_URL}/shipment/list", json={}, headers=sf_staff_headers)
        assert response.status_code == 200
        sf_shipments = response.json()["results"]
        sf_shipment_ids = [s["id"] for s in sf_shipments]
        assert shipment_id in sf_shipment_ids
        
        la_staff_token = auth_tokens["StaffAtLos Angeles Warehouse"]
        la_staff_headers = {"Authorization": f"Bearer {la_staff_token}"}
        
        response = requests.post(f"{BASE_URL}/shipment/list", json={}, headers=la_staff_headers)
        assert response.status_code == 200
        la_shipments = response.json()["results"]
        la_shipment_ids = [s["id"] for s in la_shipments]
        assert shipment_id in la_shipment_ids
        
        carrier_token = auth_tokens["Carrier1"]
        carrier_headers = {"Authorization": f"Bearer {carrier_token}"}
        
        response = requests.post(f"{BASE_URL}/shipment/list", json={}, headers=carrier_headers)
        assert response.status_code == 200
        carrier_shipments = response.json()["results"]
        carrier_shipment_ids = [s["id"] for s in carrier_shipments]
        assert shipment_id in carrier_shipment_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])