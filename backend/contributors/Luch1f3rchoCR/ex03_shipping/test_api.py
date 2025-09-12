import pytest
from backend.contributors.Luch1f3rchoCR.ex03_shipping.main import app
from backend.contributors.Luch1f3rchoCR.ex03_shipping.database import init_db, SessionLocal
from backend.contributors.Luch1f3rchoCR.ex03_shipping.models import User

def _ensure_admin():
    init_db()
    with SessionLocal() as db:
        u = db.query(User).filter(User.username == "admin").one_or_none()
        if not u:
            db.add(User(username="admin", password="admin", role="admin"))
            db.commit()

@pytest.fixture
def client():
    _ensure_admin()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def test_login_and_list_shipments(client):
    r = client.post("/login", json={"username": "admin", "password": "admin"})
    assert r.status_code == 200
    data = r.get_json()
    token = data.get("token") or data.get("access_token")
    assert token

    r2 = client.post(
        "/shipment/list",
        headers={"Authorization": f"Bearer {token}"},
        json={}
    )
    assert r2.status_code == 200
    assert isinstance(r2.get_json(), list)