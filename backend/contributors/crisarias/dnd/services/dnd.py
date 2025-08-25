import requests
from flask import current_app
from services.telemetry import setupLogger

logger = setupLogger()


def getMonsters():
     try:
        base_url = current_app.config.get('DND_API_BASE_URL')
        url = f"{base_url}/api/2014/monsters"
        response = requests.get(url)
        data = response.json()
        results = data.get('results')
        if not results:
            return None, response.status_code
        return results, response.status_code
     except Exception as e:
        logger.error(f"Error fetching monsters: {e}")
        return None, 500

def getMonsterById(index):
    try:
        base_url = current_app.config.get('DND_API_BASE_URL')
        url = f"{base_url}/api/2014/monsters/{index}"
        response = requests.get(url)
        data = response.json()
        return data, response.status_code
    except Exception as e:
        logger.error(f"Error fetching monster by id {index}: {e}")
        return None, 500