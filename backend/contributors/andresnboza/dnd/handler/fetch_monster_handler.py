import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))

from database import get_session
from .base_handler import Handler
from schemas.monster_request_schema import MonsterRequestSchema

from models import AndresnbozaMonster

from marshmallow import ValidationError
import requests

from utils.logger import log_message

class FetchMonsterHandler(Handler):

    url = "https://www.dnd5eapi.co/api/2014/monsters"
    headers = {
        'Accept': 'application/json'
    }
    payload = {}

    @staticmethod
    def normalize_monster_name(name):
        return name.lower().replace('-', ' ')

    def handle(self, request):
        schema = MonsterRequestSchema()
        try:
            validated = schema.load(request)
        except ValidationError as err:
            return {"error": err.messages}

        monster_index = validated['monster_index']
        normalized_name = self.normalize_monster_name(monster_index)

        log_message(f"Normalized monster name: {normalized_name}")

        session = get_session()

        monster = session.query(AndresnbozaMonster).filter_by(name=normalized_name).first()
        log_message(f"Local DB lookup for monster '{normalized_name}': {'Found' if monster else 'Not Found'}")

        if monster:
            result = {"monster": monster.to_dict(), "source": "local_db"}
        else:
            # Fetch from external API
            newUrl = self.url + f"/{monster_index}"
            response = requests.request("GET", newUrl, headers=self.headers, data=validated)
            log_message(f"Fetched monster data: {response.text}")

            if response.status_code == 200:
                monster_data = response.json()
                # Insert into DB
                new_monster = AndresnbozaMonster.from_api_data(monster_data, self.normalize_monster_name)
                session.add(new_monster)
                session.commit()
                result = {"monster": new_monster.to_dict(), "source": "external_api"}
            else:
                result = {"error": "Monster not found in external API"}
                result['status_code'] = 404
        session.close()
        return result