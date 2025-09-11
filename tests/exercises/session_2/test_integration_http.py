import os
import requests
import pytest

optional = pytest.mark.xfail(reason="optional test", strict=False)

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


@optional
def test_sushi_ramen_extra():
    url = f"{API_URL}/people/sushi_ramen"
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload == {"success": True, "data": 0}


@optional
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


@optional
def test_most_common_food_overall_extra():
    url = f"{API_URL}/people/most_common_food_overall"
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload == {"success": True, "data": "curry"}


@optional
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
        "brazilian-black": 75.20,
        "brazilian-blonde": 98,
        "brazilian-brown": 68,
        "brazilian-gray": 87,
        "brazilian-red": 84.50,
        "canadian-auburn": 74.25,
        "canadian-black": 93,
        "canadian-brown": 72,
        "canadian-gray": 74,
        "canadian-red": 56.25,
        "french-auburn": 82.75,
        "french-black": 85.50,
        "french-brown": 82,
        "french-red": 79.50,
        "german-auburn": 65,
        "german-black": 60,
        "german-blonde": 73.50,
        "german-brown": 70.17,
        "mexican-auburn": 64,
        "mexican-blonde": 63,
        "mexican-brown": 96,
        "mexican-gray": 97,
        "mexican-red": 73,
        "nigerian-auburn": 81,
        "nigerian-black": 71.50,
        "nigerian-blonde": 60.33,
        "nigerian-brown": 54,
        "nigerian-gray": 85,
        "nigerian-red": 76.50,
        "spanish-black": 79,
        "spanish-gray": 61,
        "spanish-red": 67.50,
    }

    assert payload == {"success": True, "data": expected}


@optional
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
        "French": ["Nicholas Perez", "John Byrd"],
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


@optional
def test_top_hobbies_extra():
    url = f"{API_URL}/people/top_hobbies"
    resp = requests.get(url, timeout=10)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload == {"success": True, "data": ["Alexander Jensen", "Amy Graham", "Amy James"]}


@optional
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
        "german": 179.10,
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
