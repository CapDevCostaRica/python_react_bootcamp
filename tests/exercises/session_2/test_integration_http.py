import os
import requests
import pytest

API_URL = os.environ.get("API_URL", "http://127.0.0.1:4000")


def post_find(filters):
    url = f"{API_URL}/people/find"
    # encode filters as query params: filters[key]=value
    params = {f"filters[{k}]": v for k, v in (filters or {}).items()}
    resp = requests.get(url, params=params, timeout=10)
    return resp


def assert_success_data(resp):
    assert resp.status_code == 200
    payload = resp.json()
    assert payload.get("success") is True
    data = payload.get("data")
    assert isinstance(data, dict)
    assert "total" in data and "results" in data


@pytest.mark.parametrize(
    "filters,expected",
    [
        (
            {
                "eye_color": "hazel",
                "hair_color": "black",
                "degree": "PhD",
                "hobby": "dancing",
                "food": "lasagna",
                "family": "mother",
            },
            ["Regina Fisher", "Emily Boyd"],
        ),
        (
            {
                "eye_color": "green",
                "hair_color": "black",
                "degree": "Certificate",
                "hobby": "chess",
                "food": "salad",
                "family": "aunt",
            },
            ["Dennis Mills", "Keith Jackson"],
        ),
        (
            {
                "eye_color": "blue",
                "hair_color": "brown",
                "nationality": "Mexican",
            },
            ["Mark Sullivan"],
        ),
        (
            {
                "eye_color": "hazel",
                "hair_color": "black",
                "age": 39,
                "nationality": "Spanish",
            },
            ["Regina Fisher"],
        ),
        (
            {
                "eye_color": "green",
                "hair_color": "brown",
                "age": 25,
            },
            ["Sarah Flores"],
        ),
    ],
)
def test_search_cases_http(filters, expected):
    resp = post_find(filters)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload.get("success") is True
    data = payload.get("data", {})
    print(data)
    assert isinstance(data, dict)
    assert "total" in data and "results" in data
    assert data.get("total") == len(expected)
    results = data.get("results", [])
    assert set(results) == set(expected)


def test_sushi_ramen_extra():
    url = f"{API_URL}/people/sushi_ramen"
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload == {"success": True, "data": 0}


def test_avg_weight_above_70_hair_extra():
    url = f"{API_URL}/people/avg_weight_above_70_hair"
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload.get("success") is True
    data = payload.get("data")
    assert isinstance(data, dict)
    expected = {
        "auburn": 73.52,
        "black": 78.12,
        "brown": 77.84,
        "gray": 76.67,
        "red": 70.35,
    }
    for k, v in expected.items():
        assert k in data, f"missing key {k}"
        assert pytest.approx(data.get(k), rel=1e-3) == v


def test_most_common_food_overall_extra():
    url = f"{API_URL}/people/most_common_food_overall"
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload == {"success": True, "data": "curry"}


def test_avg_weight_nationality_hair_extra():
    url = f"{API_URL}/people/avg_weight_nationality_hair"
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200
    payload = resp.json()

    expected = {
        "american-auburn": 67,
        "american-black": 78,
        "american-blonde": 70,
        "american-brown": 94,
        "american-gray": 75,
        "american-red": 74,
        "brazilian-auburn": 70,
        "brazilian-black": 75,
        "brazilian-blonde": 98,
        "brazilian-brown": 68,
        "brazilian-gray": 87,
        "canadian-auburn": 75,
        "canadian-black": 70,
        "canadian-blonde": 67,
        "canadian-brown": 66,
        "canadian-gray": 70,
        "french-auburn": 74,
        "french-black": 88,
        "french-blonde": 68,
        "french-brown": 78,
        "french-gray": 77,
        "german-auburn": 83,
        "german-black": 76,
        "german-blonde": 78,
        "german-brown": 87,
        "german-gray": 85,
        "mexican-auburn": 73,
        "mexican-black": 80,
        "mexican-blonde": 81,
        "mexican-brown": 75,
        "mexican-gray": 80,
        "nigerian-auburn": 74,
        "nigerian-black": 71,
        "nigerian-blonde": 73,
        "nigerian-brown": 76,
        "nigerian-gray": 64,
        "spanish-auburn": 58,
        "spanish-black": 85,
        "spanish-blonde": 72,
        "spanish-brown": 79,
        "spanish-gray": 76,
    }

    assert payload == {"success": True, "data": expected}


def test_top_oldest_nationality_extra():
    url = f"{API_URL}/people/top_oldest_nationality"
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload.get("success") is True
    data = payload.get("data")
    assert isinstance(data, dict)
    expected = {
        "American": ["Andre Newman", "Samantha Mathis"],
        "Brazilian": ["Robert Leonard", "Emily Martinez"],
        "Canadian": ["Stephen Thompson", "Zachary Diaz"],
        "French": ["Nicholas Perez", "Lisa Miller"],
        "German": ["Alexander Jensen", "Yvonne Marshall"],
        "Mexican": ["Paul Kelly", "Kimberly Mayer"],
        "Nigerian": ["Logan Lee", "Jack Owens MD"],
        "Spanish": ["William Hurley", "Richard Howard"],
    }
    for nat, names in expected.items():
        assert nat in data, f"missing nationality {nat} in response"
        val = data.get(nat)
        assert isinstance(val, list), f"expected list for {nat}"
        for n in names:
            assert n in val, f"expected {n} in top list for {nat}"


def test_top_hobbies_extra():
    url = f"{API_URL}/people/top_hobbies"
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload == {"success": True, "data": ["Danny Smith", "Melissa Lee", "Logan Lee"]}


def test_avg_height_nationality_general_extra():
    url = f"{API_URL}/people/avg_height_nationality_general"
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload.get("success") is True
    data = payload.get("data")
    assert isinstance(data, dict)

    expected_general = 176.34
    expected_nationalities = {
        "american": 179.67,
        "brazilian": 175.83,
        "canadian": 175.27,
        "french": 173.54,
        "german": 179.1,
        "mexican": 178.09,
        "nigerian": 168.54,
        "spanish": 183.0,
    }

    assert "general" in data
    assert pytest.approx(data.get("general"), rel=1e-3) == expected_general

    nationalities = data.get("nationalities")
    assert isinstance(nationalities, dict)
    for k, v in expected_nationalities.items():
        assert k in nationalities, f"missing nationality {k}"
        assert pytest.approx(nationalities.get(k), rel=1e-3) == v

