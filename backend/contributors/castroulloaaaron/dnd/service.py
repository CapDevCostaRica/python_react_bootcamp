from backend.contributors.castroulloaaaron.dnd.api import API


class Service:
    def __init__(self, api=API()):
        self._api = api

    def list(self, payload: dict):
        pass

    def get(self, payload: dict):
        pass
