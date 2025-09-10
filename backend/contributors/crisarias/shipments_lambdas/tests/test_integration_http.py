import os
import requests
import pytest

optional = pytest.mark.xfail(reason="optional test", strict=False)

API_URL = os.environ.get("API_URL", "http://127.0.0.1:4000")

def get_auth_token(username):
    url = f"{API_URL}/login"
    data = {
        "username": username,
    }
    resp = requests.post(url, json=data)
    if resp.status_code == 200:
        return resp.json().get("token")
    return None

def get_auth_headers(username):
    token = get_auth_token(username)
    if token:
        return {
            "Authorization": f"Bearer {token}"
        }
    return {}

def test_login():
    url = f"{API_URL}/login"
    data = {
        "username": "GlobalManager",
    }
    resp = requests.post(url, json=data)
    assert resp.status_code == 200
    assert resp.json().get("token") is not None
    assert resp.json().get("token_type") == "Bearer"

def test_login_invalid_user():
    url = f"{API_URL}/login"
    data = {
        "username": "InvalidUser",
    }
    resp = requests.post(url, json=data)
    assert resp.status_code == 404
    assert resp.json().get("error") == "Invalid username"

def test_list_shipments_no_auth():
    url = f"{API_URL}/shipment/list"
    data = {}
    resp = requests.post(url, json=data)
    assert resp.status_code == 401
    assert resp.json().get("error") == "Unauthorized: Missing or invalid Authorization header."

def test_create_shipments_no_auth():
    url = f"{API_URL}/shipment"
    data = {}
    resp = requests.post(url, json=data)
    assert resp.status_code == 401
    assert resp.json().get("error") == "Unauthorized: Missing or invalid Authorization header."

def test_update_shipments_no_auth():
    url = f"{API_URL}/shipment/1"
    data = {}
    resp = requests.post(url, json=data)
    assert resp.status_code == 401
    assert resp.json().get("error") == "Unauthorized: Missing or invalid Authorization header."

def test_create_shipments_invalid_roles():
    headers = get_auth_headers("GlobalManager")
    url = f"{API_URL}/shipment"
    data = {}
    resp = requests.post(url, json=data, headers=headers)
    assert resp.status_code == 403
    assert resp.json().get("error") == "Forbidden: You do not have the required role."
    headers = get_auth_headers("Carrier1")
    resp = requests.post(url, json=data, headers=headers)
    assert resp.status_code == 403
    assert resp.json().get("error") == "Forbidden: You do not have the required role."
    headers = get_auth_headers("ManagerAtLos Angeles Warehouse")
    resp = requests.post(url, json=data, headers=headers)
    assert resp.status_code == 403
    assert resp.json().get("error") == "Forbidden: You do not have the required role."

def test_update_shipments_invalid_roles():
    headers = get_auth_headers("GlobalManager")
    url = f"{API_URL}/shipment/1"
    data = {}
    resp = requests.post(url, json=data, headers=headers)
    assert resp.status_code == 403
    assert resp.json().get("error") == "Forbidden: You do not have the required role."
    headers = get_auth_headers("ManagerAtLos Angeles Warehouse")
    resp = requests.post(url, json=data, headers=headers)
    assert resp.status_code == 403
    assert resp.json().get("error") == "Forbidden: You do not have the required role."

def test_list_shipments_with_auth():
    headers = get_auth_headers("GlobalManager")
    url = f"{API_URL}/shipment/list"
    resp = requests.get(url, headers=headers)
    assert resp.status_code == 200
    assert resp.json().get("result_count") == len(resp.json().get("results"))
    assert isinstance(resp.json().get("results"), list)

@optional
def test_create_shipments_with_auth():
    headers = get_auth_headers("StaffAtSan Francisco Warehouse")
    url = f"{API_URL}/shipment"
    data = {
        "origin_warehouse": 1,
        "target_warehouse": 2,
        "carrier": 10
    }
    resp = requests.post(url, json=data, headers=headers)
    assert resp.status_code == 201

@optional
def test_update_shipment_location_with_auth():
    headers = get_auth_headers("Carrier2")
    url = f"{API_URL}/shipment/7"
    data = {
        "location": 92101
    }
    resp = requests.post(url, json=data, headers=headers)
    assert resp.status_code == 200

@optional
def test_update_shipment_status_with_auth():
    headers = get_auth_headers("StaffAtSan Diego Warehouse")
    url = f"{API_URL}/shipment/7"
    data = {
        "status": "delivered"
    }
    resp = requests.post(url, json=data, headers=headers)
    assert resp.status_code == 200
