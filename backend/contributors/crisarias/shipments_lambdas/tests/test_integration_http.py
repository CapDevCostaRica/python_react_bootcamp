import os
import requests
import pytest

optional = pytest.mark.xfail(reason="optional test", strict=False)

API_URL = os.environ.get("API_URL", "http://127.0.0.1:4000")

# TODO Add Tests for login and lists shipments

def test_login():
    url = f"{API_URL}/login"
    data = {
        "username": "GlobalManager",
    }
    resp = requests.post(url, json=data)
    assert resp.status_code == 200
    assert resp.json().get("token") is not None
    assert resp.json().get("token_type") == "Bearer"
