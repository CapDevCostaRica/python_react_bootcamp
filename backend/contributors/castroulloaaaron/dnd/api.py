import logging
import requests


class API:
    def __init__(self, base_url='https://www.dnd5eapi.co/api/monsters'):
        self._logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self._base_url = base_url

    def list(self):
        res = requests.get(self._base_url)
        if res.status_code != requests.codes.ok:
            self._logger.error(f'Error fetching data from {self._base_url}: {res.status_code} {res.text}')
            raise Exception(f'Error fetching data from {self._base_url}')

        return res.json()['results']

    def get(self, idx: str):
        res = requests.get(f'{self._base_url}/{idx}')
        if res.status_code == requests.codes.not_found:
            return None
        if res.status_code != requests.codes.ok:
            self._logger.error(f'Error fetching data from {self._base_url}/{idx}: {res.status_code} {res.text}')
            raise Exception(f'Error fetching data from {self._base_url}/{idx}')

        return res.json()
