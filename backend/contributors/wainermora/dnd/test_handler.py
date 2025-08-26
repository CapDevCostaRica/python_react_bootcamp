#!/usr/bin/env python3
"""
Test script for the handler pattern implementation.
This script tests both list and get events using POST requests.
"""

import requests
import json

# Base URL for the service
BASE_URL = "http://localhost:4000"

def test_list_endpoint():
    """Test the list endpoint with monsters resource."""
    print("Testing list endpoint...")
    
    payload = {"resource": "monsters"}
    
    try:
        response = requests.post(f"{BASE_URL}/list", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Number of monsters: {data.get('count', 0)}")
            if data.get('results'):
                print(f"First monster: {data['results'][0]['name']}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the service. Make sure it's running on localhost:4000")
    except Exception as e:
        print(f"Error: {e}")

def test_get_endpoint():
    """Test the get endpoint with a monster index."""
    print("\nTesting get endpoint...")
    
    # Using a common monster index
    payload = {"monster_index": "aboleth"}
    
    try:
        response = requests.post(f"{BASE_URL}/get", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Monster Name: {data.get('name', 'N/A')}")
            print(f"Monster Type: {data.get('type', 'N/A')}")
            print(f"Challenge Rating: {data.get('challenge_rating', 'N/A')}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the service. Make sure it's running on localhost:4000")
    except Exception as e:
        print(f"Error: {e}")

def test_invalid_payload_list():
    """Test list endpoint with invalid payload."""
    print("\nTesting list endpoint with invalid payload...")
    
    payload = {"invalid": "data"}
    
    try:
        response = requests.post(f"{BASE_URL}/list", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the service. Make sure it's running on localhost:4000")
    except Exception as e:
        print(f"Error: {e}")

def test_invalid_payload_get():
    """Test get endpoint with invalid payload."""
    print("\nTesting get endpoint with invalid payload...")
    
    payload = {"invalid": "data"}
    
    try:
        response = requests.post(f"{BASE_URL}/get", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the service. Make sure it's running on localhost:4000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Handler Pattern Test - Two Endpoints")
    print("=" * 50)
    
    test_list_endpoint()
    test_get_endpoint()
    test_invalid_payload_list()
    test_invalid_payload_get()
    
    print("\nTest completed!")
