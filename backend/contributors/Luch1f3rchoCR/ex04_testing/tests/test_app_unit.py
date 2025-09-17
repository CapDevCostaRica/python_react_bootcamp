import pytest
import requests
import contributors.Luch1f3rchoCR.ex04_testing.app.services as services

@pytest.mark.parametrize("monster_index,expected", [
    ("dragon", {"name": "Mock Dragon", "type": "dragon"}),
    ("orc", {"name": "Mock Orc", "type": "humanoid"}),
    ("troll", {"name": "Mock Troll", "type": "giant"}),
])
def test_monster_endpoint_success(client, monkeypatch, monster_index, expected):
    monkeypatch.setattr(services, "fetch_monster", lambda _: expected)
    res = client.post("/monster", json={"monster_index": monster_index})
    assert res.status_code == 200
    assert res.get_json() == expected

def test_monster_endpoint_validation_error(client):
    res = client.post("/monster", json={"monster_index": ""})
    assert res.status_code == 400

def test_monster_endpoint_external_error_returns_500(client, monkeypatch):
    def _raise(_): raise requests.ConnectionError("down")
    monkeypatch.setattr(services, "fetch_monster", _raise)
    res = client.post("/monster", json={"monster_index": "orc"})
    assert res.status_code == 500