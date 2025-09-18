import requests

def test_integration_happy_path(client, monkeypatch):
    class _Resp:
        def raise_for_status(self): pass
        def json(self): return {"name": "Ancient Red Dragon", "type": "dragon"}
    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp())
    res = client.post("/monster", json={"monster_index": "dragon"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["name"] == "Ancient Red Dragon"
    assert body["type"] == "dragon"

def test_health_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"