import requests


class API:
    def __init__(self, base_url='https://www.dnd5eapi.co/api/monsters'):
        self._base_url = base_url

    def list(self):
        res = requests.get(self._base_url)
        if res.status_code != requests.codes.ok:
            raise Exception(f'Error fetching data from {self._base_url}')

        return res.json()['results']

    def get(self, idx: str):
        res = requests.get(f'{self._base_url}/{idx}')
        if res.status_code != requests.codes.ok:
            raise Exception(f'Error fetching data from {self._base_url}/{idx}')

        return res.json()
