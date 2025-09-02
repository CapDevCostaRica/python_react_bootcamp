import os, sys, requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))

from models import alfonsovso_MonsterIndex, alfonsovso_Monster
from database import get_session

BASE_URL = "https://www.dnd5eapi.co"

def list_monsters():
    session = get_session()
    try:
        rows = session.query(alfonsovso_MonsterIndex).all()
        if rows:
            return [{"index": r.index, "name": r.name, "url": r.url} for r in rows]

        r = requests.get(f"{BASE_URL}/api/monsters", timeout=10)
        r.raise_for_status()
        results = r.json().get("results", [])

        for item in results:
            session.merge(
                alfonsovso_MonsterIndex(index=item["index"], name=item["name"], url=item["url"])
            )
        session.commit()
        return results
    finally:
        session.close()

def get_monster(monster_index: str):
    session = get_session()
    try:
        row = session.query(alfonsovso_Monster).filter_by(index=monster_index).one_or_none()
        if row:
            return row.payload

        r = requests.get(f"{BASE_URL}/api/monsters/{monster_index}", timeout=10)
        if r.status_code == 404:
            return {"error": "monster not found"}, 404
        r.raise_for_status()
        payload = r.json()

        session.merge(
            alfonsovso_Monster(index=payload["index"], name=payload["name"], payload=payload)
        )
        session.commit()
        return payload
    finally:
        session.close()
