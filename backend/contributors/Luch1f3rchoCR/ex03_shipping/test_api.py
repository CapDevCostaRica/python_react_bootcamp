import pytest
from main import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_login_and_list_shipments(client):
    # 1. Login
    login_resp = client.post("/login", json={
        "username": "admin",
        "password": "admin"
    })
    assert login_resp.status_code == 200
    token = login_resp.get_json().get("access_token")
    assert token, "Login should return a token"

    # 2. Call /shopment/list with tokn
    resp = client.post(
        "/shipment/list",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict) or isinstance(data, list)