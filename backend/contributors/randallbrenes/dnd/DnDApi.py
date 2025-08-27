from marshmallow import ValidationError
import requests
from schemas.monster import MonsterSchema
from schemas.response import ResponseListSchema
class DnDApi:
    def __init__(self):
        self._api_url = "https://www.dnd5eapi.co/api/monsters"
        self._list_schema = ResponseListSchema()
        self._get_schema = MonsterSchema()

    def list(self):
        resp = requests.get(self._api_url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            try:
                return self._list_schema.load(data)
            except ValidationError as err:
                print("Error validating list from api: ", err.messages)
                return self._list_schema.empty()
        return self._list_schema.empty()

    def get(self, monster_index: str):
        url = self._api_url + "/" + monster_index
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            monster_response = response.json()
            monster_object = {
                "index": monster_response.get("index"),
                "name": monster_response.get("name"),
                "url": monster_response.get("url"),
                "json_data": monster_response
            }
            try:
                return self._get_schema.load(monster_object)
            except ValidationError as err:
                print("Error validating get from api: ", err.messages)
                return None
            except Exception as err:
                print("Error getting monster from api: ", str(err))
                return None
        else:
            print("API request failed with code:", response.status_code, url)
        return None
    