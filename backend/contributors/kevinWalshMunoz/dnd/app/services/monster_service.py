# Monster service functions
import requests
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../framework')))
from database import get_session
from models import kevinWalshMunozMonsterList

def get_all_monsters():
    """Return a list of all monsters from the database"""
    session = get_session()
    try:
        monsters = session.query(kevinWalshMunozMonsterList).all()
        count = len(monsters)
        return {"results": monsters, "count": count}
    finally:
        session.close()

def get_monster_by_index(index):
    """Get a monster's details by its id"""
    session = get_session()
    try:
        monster = session.query(kevinWalshMunozMonsterList).filter_by(id=index).first()
        return monster
    finally:
        session.close()

def fetch_monsters_from_api():
    """Fetch monsters from external DnD API"""
    url = "https://www.dnd5eapi.co/api/2014/monsters"
    headers = {
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()
    
def bulk_insert_monsters(data: dict):
    """
    Inserta múltiples monstruos en la tabla kevinWalshMunozMonsters.
    :param data: Diccionario con la clave 'results' que contiene la lista de monstruos.
    """
    session = get_session()
    try:
        monsters = [
            kevinWalshMunozMonsterList(
                index=monster["index"],
                name=monster["name"],
                url=monster["url"]
            )
            for monster in data.get("results", [])
        ]
        session.bulk_save_objects(monsters)
        session.commit()
    finally:
        session.close()