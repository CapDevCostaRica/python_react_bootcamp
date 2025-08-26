import os
import requests


class odkeyo_UpstreamError(Exception):
    pass


class odkeyo_DnDClient:
    def __init__(self, base_url=None, timeout=None):
        self.base_url = "https://www.dnd5eapi.co/api"
        self.timeout = int(timeout or 10)

    def _get(self, path, params=None):
        url = f"{self.base_url}/{path}"
        try:
            resp = requests.get(url, params=params or {}, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            raise odkeyo_UpstreamError(str(e))

    def list_monsters(self, params=None):
        return self._get("monsters", params=params)

    def get_monster_by_index(self, index):
        return self._get(f"monsters/{index}")
