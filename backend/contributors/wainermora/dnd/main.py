import os
import sys
import requests
import json
from flask import Flask, request, jsonify
from marshmallow import ValidationError

# Add framework path to import models and database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))

from database import get_session
from models import WainerMora_Monsters
from schemas import (
    ListRequestSchema, 
    GetRequestSchema, 
    MonsterSchema, 
    MonsterListResponseSchema, 
    ErrorSchema
)

app = Flask(__name__)

# D&D 5e API base URL
DND_API_BASE_URL = "https://www.dnd5eapi.co/api"

# Schema instances
list_request_schema = ListRequestSchema()
get_request_schema = GetRequestSchema()
monster_schema = MonsterSchema()
monster_list_schema = MonsterListResponseSchema()
error_schema = ErrorSchema()


def fetch_monsters_from_api():
    """Fetch all monsters from the D&D 5e API."""
    try:
        response = requests.get(f"{DND_API_BASE_URL}/2014/monsters")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        app.logger.error(f"Error fetching monsters from API: {e}")
        return None


def fetch_monster_by_index_from_api(monster_index):
    """Fetch a specific monster by index from the D&D 5e API."""
    try:
        response = requests.get(f"{DND_API_BASE_URL}/monsters/{monster_index}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        app.logger.error(f"Error fetching monster {monster_index} from API: {e}")
        return None


def save_monster_to_db(monster_data):
    """Save monster data to the database."""
    session = get_session()
    try:
        # Check if monster already exists
        existing_monster = session.query(WainerMora_Monsters).filter_by(index=monster_data['index']).first()
        if existing_monster:
            return existing_monster
        
        # Create new monster record
        monster = WainerMora_Monsters(
            index=monster_data['index'],
            name=monster_data['name'],
            size=monster_data.get('size'),
            type=monster_data.get('type'),
            subtype=monster_data.get('subtype'),
            alignment=monster_data.get('alignment'),
            armor_class=monster_data.get('armor_class'),
            hit_points=monster_data.get('hit_points'),
            hit_dice=monster_data.get('hit_dice'),
            hit_points_roll=monster_data.get('hit_points_roll'),
            speed=monster_data.get('speed'),
            strength=monster_data.get('strength'),
            dexterity=monster_data.get('dexterity'),
            constitution=monster_data.get('constitution'),
            intelligence=monster_data.get('intelligence'),
            wisdom=monster_data.get('wisdom'),
            charisma=monster_data.get('charisma'),
            proficiencies=monster_data.get('proficiencies'),
            damage_vulnerabilities=monster_data.get('damage_vulnerabilities'),
            damage_resistances=monster_data.get('damage_resistances'),
            damage_immunities=monster_data.get('damage_immunities'),
            condition_immunities=monster_data.get('condition_immunities'),
            senses=monster_data.get('senses'),
            languages=monster_data.get('languages'),
            challenge_rating=monster_data.get('challenge_rating'),
            proficiency_bonus=monster_data.get('proficiency_bonus'),
            xp=monster_data.get('xp'),
            special_abilities=monster_data.get('special_abilities'),
            actions=monster_data.get('actions'),
            legendary_actions=monster_data.get('legendary_actions'),
            reactions=monster_data.get('reactions'),
            forms=monster_data.get('forms'),
            spellcasting=monster_data.get('spellcasting'),
            image=monster_data.get('image'),
            url=monster_data.get('url')
        )
        
        session.add(monster)
        session.commit()
        return monster
        
    except Exception as e:
        session.rollback()
        app.logger.error(f"Error saving monster to database: {e}")
        return None
    finally:
        session.close()


@app.route('/list', methods=['POST'])
def list_endpoint():
    """List endpoint that follows the handler pattern."""
    try:
        # Get the request payload
        payload = request.get_json()
        
        if not payload:
            return jsonify(error_schema.dump({'error': 'Validation Error', 'message': 'Request body is required'})), 400
        
        # Validate the list request
        try:
            data = list_request_schema.load(payload)
        except ValidationError as e:
            return jsonify(error_schema.dump({'error': 'Validation Error', 'message': str(e.messages)})), 400
        
        session = get_session()
        try:
            # Check if we have monsters in local DB
            monsters = session.query(WainerMora_Monsters).all()
            
            if monsters:
                # Return from cache
                app.logger.info("Returning monsters from cache")
                results = []
                for monster in monsters:
                    results.append({
                        'index': monster.index,
                        'name': monster.name,
                        'url': f"/api/monsters/{monster.index}"
                    })
                
                response_data = {
                    'count': len(results),
                    'results': results
                }
                return jsonify(monster_list_schema.dump(response_data))
            
            else:
                # Fetch from API and cache
                app.logger.info("Fetching monsters from D&D API")
                api_data = fetch_monsters_from_api()
                
                if not api_data:
                    return jsonify(error_schema.dump({'error': 'API Error', 'message': 'Unable to fetch monsters from upstream API'})), 502
                
                # For the list endpoint, we only need to store basic info
                # The detailed info will be fetched and cached when individual monsters are requested
                results = []
                for item in api_data.get('results', []):
                    # Create minimal monster record for list caching
                    existing_monster = session.query(WainerMora_Monsters).filter_by(index=item['index']).first()
                    if not existing_monster:
                        monster = WainerMora_Monsters(
                            index=item['index'],
                            name=item['name'],
                            url=item['url']
                        )
                        session.add(monster)
                    
                    results.append({
                        'index': item['index'],
                        'name': item['name'],
                        'url': f"/v1/api/monsters/{item['index']}"
                    })
                
                session.commit()
                
                response_data = {
                    'count': len(results),
                    'results': results
                }
                return jsonify(monster_list_schema.dump(response_data))
                
        except Exception as e:
            session.rollback()
            app.logger.error(f"Error in list_endpoint: {e}")
            return jsonify(error_schema.dump({'error': 'Internal Server Error', 'message': 'An error occurred while processing the request'})), 500
        finally:
            session.close()
            
    except Exception as e:
        app.logger.error(f"Error in list_endpoint: {e}")
        return jsonify(error_schema.dump({'error': 'Internal Server Error', 'message': 'An error occurred while processing the request'})), 500


@app.route('/get', methods=['POST'])
def get_endpoint():
    """Get endpoint that follows the handler pattern."""
    try:
        # Get the request payload
        payload = request.get_json()
        
        if not payload:
            return jsonify(error_schema.dump({'error': 'Validation Error', 'message': 'Request body is required'})), 400
        
        # Validate the get request
        try:
            data = get_request_schema.load(payload)
            monster_index = data['monster_index']
        except ValidationError as e:
            return jsonify(error_schema.dump({'error': 'Validation Error', 'message': str(e.messages)})), 400
        
        session = get_session()
        try:
            # Check if monster exists in local DB with full data
            monster = session.query(WainerMora_Monsters).filter_by(index=monster_index).first()
            
            if monster and monster.type:  # Check if we have full data (type is required for complete monster)
                # Return from cache
                app.logger.info(f"Returning monster {monster_index} from cache")
                return jsonify(monster_schema.dump(monster))
            
            else:
                # Fetch from API and cache
                app.logger.info(f"Fetching monster {monster_index} from D&D API")
                api_data = fetch_monster_by_index_from_api(monster_index)
                
                if not api_data:
                    return jsonify(error_schema.dump({'error': 'Not Found', 'message': f'WainerMora_Monsters with index "{monster_index}" not found'})), 404
                
                # Save or update monster in database
                if monster:
                    # Update existing record with full data
                    for key, value in api_data.items():
                        if hasattr(monster, key):
                            setattr(monster, key, value)
                else:
                    # Create new monster record
                    monster = save_monster_to_db(api_data)
                    
                if not monster:
                    return jsonify(error_schema.dump({'error': 'Database Error', 'message': 'Unable to save monster data'})), 500
                
                session.commit()
                return jsonify(monster_schema.dump(monster))
                
        except Exception as e:
            session.rollback()
            app.logger.error(f"Error in get_endpoint: {e}")
            return jsonify(error_schema.dump({'error': 'Internal Server Error', 'message': 'An error occurred while processing the request'})), 500
        finally:
            session.close()
            
    except Exception as e:
        app.logger.error(f"Error in get_endpoint: {e}")
        return jsonify(error_schema.dump({'error': 'Internal Server Error', 'message': 'An error occurred while processing the request'})), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'service': 'dnd-proxy'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
