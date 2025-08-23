from marshmallow import ValidationError
from dnd.api import API
from dnd.validators import list_schema, get_schema
from requests import codes


class Service:
    def __init__(self, api=API()):
        self._api = api

    def list(self, payload: dict):
        try:
            list_schema.load(payload)
            return self._api.list(), codes.ok
        except ValidationError as e:
            return {'errors': e.messages}, codes.bad_request

    def get(self, payload: dict):
        try:
            get_schema.load(payload)
            return self._api.get(payload['monster_index']), codes.ok
        except ValidationError as e:
            return {'error': e.messages}, codes.bad_request
        pass
