import os
import requests

def validate_monster_index(idx: str) -> None:
    if not isinstance(idx, str) or not idx.strip():
        raise ValueError("Invalid monster index")

DND_API_BASE = os.getenv("DND_API_BASE", "https://www.dnd5eapi.co/api")
EXTERNAL_API_TIMEOUT = int(os.getenv("EXTERNAL_API_TIMEOUT", "5"))

def fetch_monster(idx: str) -> dict:
    r = requests.get(f"{DND_API_BASE}/monsters/{idx}", timeout=EXTERNAL_API_TIMEOUT)
    r.raise_for_status()
    return r.json()