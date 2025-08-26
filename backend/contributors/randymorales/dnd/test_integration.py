import requests
import pytest


BASE_URL = "http://localhost:4000"

@pytest.fixture(scope="module")
def monsters_list():
    payload = {"resource": "monsters"}
    response = requests.post(f"{BASE_URL}/list", json=payload, timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "results" in data
    assert isinstance(data["results"], list)
    return data

def test_monsters_list(monsters_list):
    # Already validated in fixture, just check count > 0
    assert monsters_list["count"] > 0
    assert len(monsters_list["results"]) == monsters_list["count"]

def test_monsters_get(monsters_list):
    # Pick a known monster index from the list
    monster_index = monsters_list["results"][0]["index"]
    payload = {"monster_index": monster_index}
    response = requests.post(f"{BASE_URL}/get", json=payload, timeout=10)
    assert response.status_code == 200
    data = response.json()
    assert data["index"] == monster_index
    assert "name" in data
    assert "type" in data

def test_monsters_get_not_found():
    payload = {"monster_index": "not-a-real-monster"}
    response = requests.post(f"{BASE_URL}/get", json=payload, timeout=10)
    assert response.status_code == 502 or response.status_code == 404
    data = response.json()
    assert "error" in data

def test_monsters_list_invalid():
    payload = {"resource": "not-monsters"}
    response = requests.post(f"{BASE_URL}/list", json=payload, timeout=10)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data

def test_monsters_get_invalid():
    payload = {"wrong_key": "bat"}
    response = requests.post(f"{BASE_URL}/get", json=payload, timeout=10)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
