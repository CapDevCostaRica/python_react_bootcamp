from flask import Flask, request, jsonify
import os
import sys
import logging
from sqlalchemy import func, desc, and_

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from seeds import seed_database
from app.models import Person, PhysicalAttribute, FamilyRelation, FavoriteFood, Hobby, Education
from database import get_session

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def health():
    return {'status': 'ok'}

@app.route('/people/find', methods=['GET'])
def find_people():
    """
    Find people based on specified filters.
    """

    if request.is_json:
        filters = request.json.get('filters', {})
    else:
        # Extract filters from query params
        filters = {}
        for key, value in request.args.items():
            # Check if key is in format filters[something]
            if key.startswith('filters[') and key.endswith(']'):
                # Extract the actual filter key
                filter_key = key[8:-1]  # Remove 'filters[' and ']'
                filters[filter_key] = value
            # Also check direct parameters (not in filters[...] format)
            elif key in ["eye_color", "hair_color", "age", "height_cm", "weight_kg", "nationality", 
                       "family", "food", "hobby", "degree", "institution"]:
                filters[key] = value
                
        logger.info(f"Extracted filters: {filters}")
    
    session = get_session()
    
    try:
        query = session.query(Person)
        
        if any(attr in filters for attr in ["eye_color", "hair_color", "age", "height_cm", "weight_kg", "nationality"]):
            query = query.join(PhysicalAttribute)
            
            if "eye_color" in filters:
                query = query.filter(PhysicalAttribute.eye_color == filters["eye_color"])
                logger.info(f"filter by eye_color: {filters['eye_color']}")
            
            if "hair_color" in filters:
                query = query.filter(PhysicalAttribute.hair_color == filters["hair_color"])
                logger.info(f"filter by hair_color: {filters['hair_color']}")
            
            if "age" in filters:
                try:
                    age = int(filters["age"])
                    query = query.filter(PhysicalAttribute.age == age)
                    logger.info(f"filter by age: {age}")
                except ValueError:
                    logger.error(f"Invalid age value: {filters['age']}")
            
            if "height_cm" in filters:
                try:
                    height = int(filters["height_cm"])
                    query = query.filter(PhysicalAttribute.height_cm == height)
                    logger.info(f"filter by height_cm: {height}")
                except ValueError:
                    logger.error(f"Invalid height_cm value: {filters['height_cm']}")
            
            if "weight_kg" in filters:
                try:
                    weight = int(filters["weight_kg"])
                    query = query.filter(PhysicalAttribute.weight_kg == weight)
                    logger.info(f"filter by weight_kg: {weight}")
                except ValueError:
                    logger.error(f"Invalid weight_kg value: {filters['weight_kg']}")
            
            if "nationality" in filters:
                query = query.filter(PhysicalAttribute.nationality == filters["nationality"])
                logger.info(f"filter by nationality: {filters['nationality']}")
        
        if "family" in filters:
            query = query.join(FamilyRelation).filter(
                FamilyRelation.relation_type == filters["family"]
            )
            logger.info(f"filter by family: {filters['family']}")
        
        if "food" in filters:
            query = query.join(FavoriteFood).filter(
                FavoriteFood.food == filters["food"]
            )
            logger.info(f"filter by food: {filters['food']}")
        
        if "hobby" in filters:
            query = query.join(Hobby).filter(
                Hobby.hobby == filters["hobby"]
            )
            logger.info(f"filter by hobby: {filters['hobby']}")
        
        if "degree" in filters or "institution" in filters:
            query = query.join(Education)
            
            if "degree" in filters:
                query = query.filter(Education.degree == filters["degree"])
                logger.info(f"filter by degree: {filters['degree']}")
            
            if "institution" in filters:
                query = query.filter(Education.institution == filters["institution"])
                logger.info(f"filter by institution: {filters['institution']}")
        
        results = query.all()
        logger.info(f"Results: {len(results)}")
        
        return jsonify({
            "success": True,
            "data": {
                "total": len(results),
                "results": [person.full_name for person in results]
            }
        })
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        session.close()


@app.route('/people/sushi_ramen', methods=['GET'])
def sushi_ramen_lovers():
    """
    People who like both sushi and ramen
    """
    session = get_session()
    try:

        people_ids = session.query(FavoriteFood.person_id)\
            .filter(FavoriteFood.food.in_(["sushi", "ramen"]))\
            .group_by(FavoriteFood.person_id)\
            .having(func.count(func.distinct(FavoriteFood.food)) == 2)\
            .all()
        
        count = len(people_ids)
        
        return jsonify({
            "success": True,
            "data": count
        })
    except Exception as e:
        logger.error(f"Error in endpoint sushi_ramen: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        session.close()


if __name__ == '__main__':
    print("Seeding database...")
    seed_database()
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=4000, debug=True)