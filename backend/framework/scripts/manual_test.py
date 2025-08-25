import requests

list_path = "/"
get_path = "/monsters"
list_url = f"http://localhost:4000{list_path}"
get_url = f"http://localhost:4000{get_path}"

def try_monsters_list():
    print("CALLING LIST MONSTERS")
    payload = {"resource": "monsters"}
    response = requests.post(
        list_url,
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
    assert original_response.json() == response.json(), f"got {response.json()} but expected {original_response.json()}"    

def try_monsters_get():
    print("CALLING GET ENDPOINT")
    payload = {"monster_index": "bat"}
    response = requests.post(
        get_url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    url = "https://www.dnd5eapi.co/api/2014/monsters/bat"
    headers = {
    'Accept': 'application/json'
    }
    original_response = requests.request("GET", url, headers=headers, data=payload)
    assert original_response.json() == response.json(), f"got {response.json()} but expected {original_response.json()}"

try_monsters_list()
try_monsters_get()