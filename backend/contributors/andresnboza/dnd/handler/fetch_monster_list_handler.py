import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))

from .base_handler import Handler
from schemas.monster_list_request_schema import MonsterListRequestSchema
from marshmallow import ValidationError
import requests

from utils.logger import log_message

class FetchMonsterListHandler(Handler):

    url = "https://www.dnd5eapi.co/api/2014/monsters"
    headers = {
        'Accept': 'application/json'
    }
    payload = {}

    def handle(self, request):
        schema = MonsterListRequestSchema()
        try:
            validated = schema.load(request)
        except ValidationError as err:
            return {"error": err.messages}

        response = requests.request("GET", self.url, headers=self.headers, data=validated)
        # log_message(f"Fetched monster data: {response.text}")

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch monster list"}