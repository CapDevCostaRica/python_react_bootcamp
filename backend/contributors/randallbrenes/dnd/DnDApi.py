import requests

class DnDApi:
    def __init__(self):
        self._api_url = "https://www.dnd5eapi.co/api/monsters"

    def list(self):
        response = requests.get(self._api_url)
        if response.status_code == 200:
            data = response.json()
            return data['results']
        return None

    def get(self, monster_index: str):
        response = requests.get(self._api_url + "/" + monster_index)
        if response.status_code == 200:
            monster_response = response.json()
            return monster_response
        return None