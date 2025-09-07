import pytest
from backend.contributors.Luch1f3rchoCR.ex03_shipping.main import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def test_login_and_list_shipments(client):
    # 1) Login
    r = client.post("/login", json={"username": "admin", "password": "admin"})
    assert r.status_code == 200
    token = r.get_json().get("token")   # toekn
    assert token, "Login should return a token"


    r2 = client.post("/shipment/list", headers={"Authorization": f"Bearer {token}"}, json={})
    assert r2.status_code == 200
    assert isinstance(r2.get_json(), list)