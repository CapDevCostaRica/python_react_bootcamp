#!/usr/bin/env python3
import os
import sys
import pytest
import requests
from http import HTTPStatus

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = os.environ.get("API_URL", "http://localhost:4000")

class TestLogin():

    @pytest.mark.parametrize("username,expected_status", [
        ("GlobalManager", HTTPStatus.OK)       
    ])
    def test_login(self, username, expected_status):
        login_data = {"username": username}
        response = requests.post(f"{BASE_URL}/login", json=login_data, headers={"Content-type": "application/json"})

        assert response.status_code == expected_status

        if expected_status == HTTPStatus.OK:
            data = response.json()
            assert "access_token" in data
            assert "token_type" in data
            assert data["token_type"] == "Bearer"

    def test_login_missing_username(self):
        response = requests.post(f"{BASE_URL}/login", json={})
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_login_invalid_user(self):
        response = requests.post(f"{BASE_URL}/login", json={"username": "NonExistentUser"})
        assert response.status_code == HTTPStatus.NOT_FOUND
        data = response.json()
        assert "error" in data

    def test_login_bad_request(self):
        response = requests.post(f"{BASE_URL}/login", json={"INVALID": "FIELD"})
        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = response.json()
        assert "error" in data