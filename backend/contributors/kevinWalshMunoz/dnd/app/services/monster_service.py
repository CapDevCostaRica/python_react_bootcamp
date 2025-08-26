"""Monster service functions"""
import requests
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../framework')))
from database import get_session
from models import kevinWalshMunozMonsterList, kevinWalshMunozMonster

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
    """Get a monster's details by its index"""
    session = get_session()
    try:
        monster = session.query(kevinWalshMunozMonster).filter_by(index=index).first()
        if monster:
            monster_dict = {c.name: getattr(monster, c.name) for c in monster.__table__.columns}
            return {"monster": monster_dict}
        return None
    finally:
        session.close()

def fetch_monster_details_from_api(index: str):
    """
    Fetch details of a specific monster from the external DnD API by index.
    :param index: The monster's index (e.g., 'adult-brass-dragon')
    :return: JSON response with monster details
    """
    url = f"https://www.dnd5eapi.co/api/2014/monsters/{index}"
    headers = {
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return None
    return response.json()

# ...existing code...

def insert_monster_details(monster_data: dict):
    """
    Insert a monster with all details into the kevinWalshMunozMonster table.
    
    :param monster_data: Dictionary containing all monster details from the API
    :return: The inserted monster object
    """
    session = get_session()
    try:
        monster = kevinWalshMunozMonster(
            index=monster_data.get("index"),
            name=monster_data.get("name"),
            size=monster_data.get("size"),
            type=monster_data.get("type"),
            alignment=monster_data.get("alignment"),
            
            armor_class=monster_data.get("armor_class"),
            hit_points=monster_data.get("hit_points"),
            hit_dice=monster_data.get("hit_dice"),
            hit_points_roll=monster_data.get("hit_points_roll"),
            speed=monster_data.get("speed"),
            
            strength=monster_data.get("strength"),
            dexterity=monster_data.get("dexterity"),
            constitution=monster_data.get("constitution"),
            intelligence=monster_data.get("intelligence"),
            wisdom=monster_data.get("wisdom"),
            charisma=monster_data.get("charisma"),
            
            proficiencies=monster_data.get("proficiencies"),
            damage_vulnerabilities=monster_data.get("damage_vulnerabilities"),
            damage_resistances=monster_data.get("damage_resistances"),
            damage_immunities=monster_data.get("damage_immunities"),
            condition_immunities=monster_data.get("condition_immunities"),
            
            senses=monster_data.get("senses"),
            languages=monster_data.get("languages"),
            challenge_rating=monster_data.get("challenge_rating"),
            proficiency_bonus=monster_data.get("proficiency_bonus"),
            xp=monster_data.get("xp"),
            
            special_abilities=monster_data.get("special_abilities"),
            actions=monster_data.get("actions"),
            legendary_actions=monster_data.get("legendary_actions"),
            reactions=monster_data.get("reactions"),
            forms=monster_data.get("forms"),
            
            image=monster_data.get("image"),
            url=monster_data.get("url")
        )
        
        session.add(monster)
        session.commit()
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
    Bulk insert monsters into the kevinWalshMunozMonsters table.
    :param data: Dictionary with the 'results' key containing the list of monsters.
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