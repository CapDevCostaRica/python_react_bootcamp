import requests

def validate_monster_index(idx: str) -> None:
    if not isinstance(idx, str) or not idx.strip():
        raise ValueError("Invalid monster index")

def fetch_monster(idx: str) -> dict:
    r = requests.get(f"https://example.api/monsters/{idx}", timeout=5)
    r.raise_for_status()
    return r.json()