import requests

# Base URL for the API
BASE_URL = "http://localhost:4000"

def test_extra_credit_endpoints():
    """Test all 7 extra credit endpoints"""

    print("Testing Extra Credit Endpoints...")

    # Extra 1: People who like both sushi and ramen
    print("\n=== Extra 1: People who like both sushi and ramen ===")
    response = requests.get(f"{BASE_URL}/people/sushi_ramen")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    print(f"Count of people who like both sushi and ramen: {result.get('data', 'N/A')}")

    # Extra 2: People with average weight above 70 grouped by hair color
    print("\n=== Extra 2: Average weight above 70 by hair color ===")
    response = requests.get(f"{BASE_URL}/people/avg_weight_above_70_hair")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    print("Hair colors with average weight > 70:")
    for hair_color, avg_weight in result.get('data', {}).items():
        print(f"  {hair_color}: {avg_weight} kg")

    # Extra 3: Most common food overall
    print("\n=== Extra 3: Most common food overall ===")
    response = requests.get(f"{BASE_URL}/people/most_common_food_overall")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    print(f"Most common food: {result.get('data', 'N/A')}")

    # Extra 4: Average weight grouped by nationality and hair color
    print("\n=== Extra 4: Average weight by nationality and hair color ===")
    response = requests.get(f"{BASE_URL}/people/avg_weight_nationality_hair")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    print("Average weight by nationality-hair combination:")
    for combo, avg_weight in result.get('data', {}).items():
        print(f"  {combo}: {avg_weight} kg")

    # Extra 5: Top 2 oldest people per nationality
    print("\n=== Extra 5: Top 2 oldest people per nationality ===")
    response = requests.get(f"{BASE_URL}/people/top_oldest_nationality")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    print("Top 2 oldest people by nationality:")
    for nationality, people in result.get('data', {}).items():
        print(f"  {nationality}: {people}")

    # Extra 6: People ranked by how many hobbies they have (Top 3)
    print("\n=== Extra 6: Top 3 people by number of hobbies ===")
    response = requests.get(f"{BASE_URL}/people/top_hobbies")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    print(f"Top 3 people with most hobbies: {result.get('data', [])}")

    # Extra 7: Average height by nationality and general
    print("\n=== Extra 7: Average height by nationality and general ===")
    response = requests.get(f"{BASE_URL}/people/avg_height_nationality_general")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    data = result.get('data', {})
    print(f"General average height: {data.get('general', 'N/A')} cm")
    print("Average height by nationality:")
    for nationality, avg_height in data.get('nationalities', {}).items():
        print(f"  {nationality}: {avg_height} cm")

    print("\n=== All extra credit tests completed! ===")

if __name__ == "__main__":
    test_extra_credit_endpoints()
