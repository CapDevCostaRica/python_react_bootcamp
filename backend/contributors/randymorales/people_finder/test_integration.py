import requests

# Base URL for the API
BASE_URL = "http://localhost:4000"

def post_find(filters):
    """Helper function to send filters as query parameters"""
    url = f"{BASE_URL}/people/find"
    # encode filters as query params: filters[key]=value
    params = {f"filters[{k}]": v for k, v in (filters or {}).items()}
    resp = requests.get(url, params=params, timeout=10)
    return resp

def test_people_finder():
    """Test the people finder endpoint with the 5 test cases from the README"""

    print("Testing People Finder API...")

    # Test 1: I have hazel eyes and black hair, hold a PhD, enjoy dancing, love lasagna, and am a mother.
    print("\n=== Test 1: Hazel eyes, black hair, PhD, dancing, lasagna, mother ===")
    test1_filters = {
        "eye_color": "hazel",
        "hair_color": "black",
        "degree": "PhD",
        "hobby": "dancing",
        "food": "lasagna",
        "family": "mother"
    }
    response = post_find(test1_filters)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    # Test 2: I have green eyes and black hair, hold a Certificate, enjoy playing chess, like eating salad, and I am an aunt.
    print("\n=== Test 2: Green eyes, black hair, Certificate, chess, salad, aunt ===")
    test2_filters = {
        "eye_color": "green",
        "hair_color": "black",
        "degree": "Certificate",
        "hobby": "chess",
        "food": "salad",
        "family": "aunt"
    }
    response = post_find(test2_filters)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    # Test 3: I have blue eyes and brown hair, and I'm from Mexico.
    print("\n=== Test 3: Blue eyes, brown hair, Mexico ===")
    test3_filters = {
        "eye_color": "blue",
        "hair_color": "brown",
        "nationality": "Mexican"
    }
    response = post_find(test3_filters)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    # Test 4: I have hazel eyes and black hair; I'm 39 years old, and I'm from Spain.
    print("\n=== Test 4: Hazel eyes, black hair, 39 years old, Spain ===")
    test4_filters = {
        "eye_color": "hazel",
        "hair_color": "black",
        "age": 39,
        "nationality": "Spanish"
    }
    response = post_find(test4_filters)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    # Test 5: I have green eyes and brown hair, and I'm 25 years old.
    print("\n=== Test 5: Green eyes, brown hair, 25 years old ===")
    test5_filters = {
        "eye_color": "green",
        "hair_color": "brown",
        "age": 25
    }
    response = post_find(test5_filters)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    # Test with no filters (should return all people)
    print("\n=== Test 6: No filters (all people) ===")
    test6_filters = {}
    response = post_find(test6_filters)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Total people found: {result['data']['total']}")

    print("\n=== All tests completed! ===")

if __name__ == "__main__":
    test_people_finder()
