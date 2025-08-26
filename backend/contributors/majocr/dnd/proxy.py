from flask import Flask, request, jsonify

import sys
import os
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from models import Monster_majocr
from database import get_session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../majocr/dnd')))
from schema import MonsterSchema_majocr
from marshmallow import ValidationError


def list_cached_monsters():
    session = get_session()
    monsters = session.query(Monster_majocr).all()
    print(f"[DOWNSTREAM] Retrieved {len(monsters)} monsters from local cache.")
    session.close()

    results = []
    for monster in monsters:
        results.append({
            "index": monster.index,
            "name": monster.name,
            "url": f"/api/2014/monsters/{monster.index}"
        })

    return {
        "count": len(results),
        "results": results
    }

def fetch_monster_from_upstream(index):
    upstream_url = f"https://www.dnd5eapi.co/api/monsters/{index}"
    print(f"[UPSTREAM] Requesting monster '{index}' from external API: {upstream_url}.")
    response = requests.get(upstream_url)

    if response.status_code != 200:
        print(f"[UPSTREAM] Failed to retrieve monster '{index}' — Status code: {response.status_code}")
        return None

    try:
        upstream_data = response.json()
        print(f"[UPSTREAM] Received data for monster '{index}': {upstream_data.get('name')}")
        return upstream_data
    except ValueError as e:
        print(f"[UPSTREAM] Failed to parse JSON for monster '{index}': {str(e)}")
        return None

def get_or_cache_monster(index):
    session = get_session()
    monster = session.query(Monster_majocr).filter_by(index=index).first()

    if monster:
        print(f"[DOWNSTREAM] Monster '{index}' found in local cache.")
        session.close()
        return unpack_monster_data(monster)
    
    # Fetch from upstream API
    try:
        upstream_data = fetch_monster_from_upstream(index)
        if not upstream_data:
            session.close()
            return {"error": f"Monster '{index}' not found in upstream API."}
        clean_data = {}
        for key in upstream_data:
            if key not in ["index", "name"]:
                clean_data[key] = upstream_data[key]
        # Validate and save to local cache
        payload = {
            "index": upstream_data.get("index"),
            "name": upstream_data.get("name"),
            "data": clean_data
        }
        validated = MonsterSchema_majocr().load(payload)
        new_monster = Monster_majocr(**validated)
        session.add(new_monster)
        session.commit()
        print(f"[DOWNSTREAM] Monster '{index}' cached successfully.")
        monster_output = unpack_monster_data(new_monster)
        session.close()
        return monster_output
    except ValidationError as error:
        print(f"[VALIDATION ERROR] Failed to validate monster '{index}': {error.messages}")
        session.close()
        return {"error": f"Validation failed for monster '{index}'", "details": str(error.messages)}
    
def unpack_monster_data(monster):
    if not monster or not monster.data:
        raise ValueError(f"Monster '{monster.name}' has no data to unpack.")
    return {
        "index": monster.index, 
        "name": monster.name, 
        **monster.data
    }