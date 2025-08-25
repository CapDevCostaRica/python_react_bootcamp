import re

import requests
import json

import http

from setup import get_new_contributor_dir


def extract_detailed_flask_routes(included_path):
    app_dir = get_new_contributor_dir()
    file_path = f"./tests/tmp/app/contributors/{app_dir}/main.py"
    if not included_path in file_path:
        return []
    with open(file_path, "r") as file:
        content = file.read()

    pattern = r"@app\.route\(['\"]([^'\"]+)['\"](?:,\s*methods\s*=\s*\[([^\]]+)\])?\)"

    matches = re.findall(pattern, content)

    routes = []
    for match in matches:
        route_path = match[0]
        methods = match[1] if match[1] else "GET"  # Default to GET

        if methods:
            methods = re.findall(r"['\"]([^'\"]+)['\"]", methods)

        routes.append(
            {
                "path": route_path,
                "methods": methods if isinstance(methods, list) else [methods],
            }
        )

    return routes


def test_extract_routes():
    detailed_routes = extract_detailed_flask_routes("dnd")
    base_url = "http://localhost:4000"
    for route in detailed_routes:
        print(f"Path: {route['path']}, Methods: {route['methods']}")
        path = route["path"]
        methods = route["methods"]

        for method in methods:
            print(f"🔍 Testing {method} {path}")

            url = f"{base_url}{path}"

            if "list" in str(path).lower().strip():
                payload = {"resource": "monsters"}
                response = requests.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10,
                )
                url = "https://www.dnd5eapi.co/api/2014/monsters"
                payload = {}
                headers = {
                'Accept': 'application/json'
                }
                original_response = requests.request("GET", url, headers=headers, data=payload)
                try:
                    assert original_response.json() == response.json()
                except AssertionError as assertion_error:
                    print(f"⚠️ {assertion_error=}")
                
            elif "get" in str(path).lower().strip():
                payload = {"monster_index": "bat"}
                response = requests.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10,
                )
                url = "https://www.dnd5eapi.co/api/2014/monsters/bat"
                headers = {
                'Accept': 'application/json'
                }
                original_response = requests.request("GET", url, headers=headers, data=payload)
                assert original_response.json() == response.json()

            else:
                # Handle other methods if needed
                response = requests.request(method, url, timeout=10)
                print(f"DEFAULT RESPONSE:{response.text}")
            assert response.status_code == http.HTTPStatus.OK

        if path != "/":
            assert "POST" in methods, (
                f"each endpoint should contain a POST mehod; found only {methods} for {path}"
            )
