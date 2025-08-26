
import os
import sys
import json
import requests
from typing import Any, Dict
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from database import get_session
from models import randymorales_MonsterCache, randymorales_MonsterListCache

UPSTREAM_BASE = "https://www.dnd5eapi.co/api/monsters"

class RandymoralesMonsterProxyService:
    """
    Service for proxying and caching D&D monster data.
    """
    def __init__(self):
        self.upstream_base = UPSTREAM_BASE

    def get_monster_list(self) -> Dict[str, Any]:
        """Get the monster list, using cache if available."""
        with get_session() as session:
            cache = session.query(randymorales_MonsterListCache).filter_by(resource='monsters').first()
            if cache:
                return json.loads(cache.list_data)
            resp = requests.get(self.upstream_base, timeout=10)
            if resp.status_code != 200:
                raise RuntimeError(f'Upstream API error: {resp.status_code} - {resp.text}')
            result = resp.json()
            session.add(randymorales_MonsterListCache(resource='monsters', list_data=json.dumps(result)))
            session.commit()
            return result

    def get_monster(self, monster_index: str) -> Dict[str, Any]:
        """Get a monster by index, using cache if available."""
        with get_session() as session:
            cache = session.query(randymorales_MonsterCache).filter_by(monster_index=monster_index).first()
            if cache:
                return json.loads(cache.monster_data)
            resp = requests.get(f"{self.upstream_base}/{monster_index}", timeout=10)
            if resp.status_code != 200:
                raise RuntimeError(f'Upstream API error: {resp.status_code} - {resp.text}')
            result = resp.json()
            session.add(randymorales_MonsterCache(monster_index=monster_index, monster_data=json.dumps(result)))
            session.commit()
            return result
