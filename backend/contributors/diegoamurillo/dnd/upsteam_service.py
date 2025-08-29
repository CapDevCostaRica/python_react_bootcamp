import requests

class UpstreamService:
    def __init__(self):
        self.base_url = 'https://www.dnd5eapi.co/api/2014/monsters'
    
    def get_monsters_list(self):
        try:
            response = requests.get(self.base_url)
            return response.json()
        except:
            return []
    
    def get_monster_by_index(self, monster_index):
        try:
            response = requests.get(f"{self.base_url}/{monster_index}")
            return response.json()

        except:
            return None