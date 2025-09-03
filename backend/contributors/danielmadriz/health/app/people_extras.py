import logging
import sys
import os
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, exists, func
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)
from models import Person, FavoriteFood, PhysicalProfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MIN_WEIGHT_THRESHOLD_KG = 70


def get_sushi_ramen_count(session: Session) -> int:
    """
    Get count of people who like both sushi and ramen.
    """
    try:
        logger.info("Starting sushi_ramen count query")
        
        all_foods = session.query(FavoriteFood.food).distinct().all()
        logger.info(f"All foods in database: {[food[0] for food in all_foods]}")
        
        sushi_count = session.query(FavoriteFood).filter(FavoriteFood.food == 'sushi').count()
        ramen_count = session.query(FavoriteFood).filter(FavoriteFood.food == 'ramen').count()
        logger.info(f"Sushi entries: {sushi_count}, Ramen entries: {ramen_count}")
        
        # Early return if either food doesn't exist in the database
        if sushi_count < 1 or ramen_count < 1:
            logger.info(f"Early return: sushi_count={sushi_count}, ramen_count={ramen_count} - cannot have people who like both")
            return 0
        
        people_count = session.query(Person).filter(
            and_(
                exists().where(
                    and_(
                        FavoriteFood.person_id == Person.id,
                        FavoriteFood.food == 'sushi'
                    )
                ),
                exists().where(
                    and_(
                        FavoriteFood.person_id == Person.id,
                        FavoriteFood.food == 'ramen'
                    )
                )
            )
        ).count()
        
        logger.info(f"Sushi_ramen query completed successfully, found {people_count} people")
        return people_count
        
    except Exception as e:
        logger.error(f"Error in get_sushi_ramen_count: {str(e)}")
        raise


def get_avg_weight_above_70_by_hair_color(session: Session) -> Dict[str, float]:
    """
    Get average weight above 70 grouped by hair color.
    """
    try:
        logger.info("Starting avg_weight_above_70_by_hair_color query")
        
        all_hair_colors = session.query(PhysicalProfile.hair_color).distinct().all()
        logger.info(f"All hair colors in database: {[color[0] for color in all_hair_colors]}")
        
        weight_count = session.query(PhysicalProfile).filter(PhysicalProfile.weight_kg.isnot(None)).count()
        logger.info(f"Total weight entries: {weight_count}")
        
        # Early return if no weight data
        if weight_count < 1:
            logger.info("Early return: no weight data available")
            return {}
        
        results = session.query(
            PhysicalProfile.hair_color,
            func.avg(PhysicalProfile.weight_kg).label('avg_weight')
        ).filter(
            PhysicalProfile.weight_kg > MIN_WEIGHT_THRESHOLD_KG
        ).group_by(
            PhysicalProfile.hair_color
        ).all()
        
        result_dict = {hair_color: float(avg_weight) for hair_color, avg_weight in results}
        
        logger.info(f"Avg weight above {MIN_WEIGHT_THRESHOLD_KG} by hair color query completed, found {len(result_dict)} hair colors")
        logger.info(f"Results: {result_dict}")
        
        return result_dict
        
    except Exception as e:
        logger.error(f"Error in get_avg_weight_above_70_by_hair_color: {str(e)}")
        raise


def get_most_common_food_overall(session: Session) -> str:
    """
    Get the most common food overall.
    """
    try:
        logger.info("Starting most_common_food_overall query")
        
        result = session.query(
            FavoriteFood.food,
            func.count(FavoriteFood.food).label('count')
        ).group_by(
            FavoriteFood.food
        ).order_by(
            func.count(FavoriteFood.food).desc()
        ).first()
        
        if result:
            most_common_food = result[0]
            count = result[1]
            logger.info(f"Most common food query completed, found '{most_common_food}' with {count} occurrences")
            return most_common_food
        else:
            logger.info("No food data found in database")
            return ""
        
    except Exception as e:
        logger.error(f"Error in get_most_common_food_overall: {str(e)}")
        raise


def get_avg_weight_by_nationality_hair_color(session: Session) -> Dict[str, float]:
    """
    Get average weight grouped by nationality and hair color.
    """
    try:
        logger.info("Starting avg_weight_by_nationality_hair_color query")
        
        weight_count = session.query(PhysicalProfile).filter(PhysicalProfile.weight_kg.isnot(None)).count()
        logger.info(f"Total weight entries: {weight_count}")
        
        if weight_count < 1:
            logger.info("Early return: no weight data available")
            return {}
        
        results = session.query(
            PhysicalProfile.nationality,
            PhysicalProfile.hair_color,
            func.avg(PhysicalProfile.weight_kg).label('avg_weight')
        ).filter(
            PhysicalProfile.weight_kg.isnot(None)
        ).group_by(
            PhysicalProfile.nationality,
            PhysicalProfile.hair_color
        ).all()
        
        result_dict = {}
        for nationality, hair_color, avg_weight in results:
            key = f"{nationality}-{hair_color}"
            result_dict[key] = float(avg_weight)
        
        logger.info(f"Avg weight by nationality-hair color query completed, found {len(result_dict)} combinations")
        logger.info(f"Results: {result_dict}")
        
        return result_dict
        
    except Exception as e:
        logger.error(f"Error in get_avg_weight_by_nationality_hair_color: {str(e)}")
        raise


def get_top_oldest_people_per_nationality(session: Session) -> Dict[str, List[str]]:

    try:
        logger.info("Starting top_oldest_people_per_nationality query")
     
        # Get all nationalities
        nationalities = session.query(PhysicalProfile.nationality).distinct().all()
        logger.info(f"Found nationalities: {[nat[0] for nat in nationalities]}")
        
        result_dict = {}
        
        for nationality_tuple in nationalities:
            nationality = nationality_tuple[0]
            
            oldest_people = session.query(
                Person.full_name
            ).join(
                PhysicalProfile, Person.id == PhysicalProfile.person_id
            ).filter(
                PhysicalProfile.nationality == nationality,
                PhysicalProfile.age.isnot(None)
            ).order_by(
                PhysicalProfile.age.desc()
            ).limit(2).all()
            
            names = [person[0] for person in oldest_people]
            result_dict[nationality] = names
            
            logger.info(f"Nationality '{nationality}': found {len(names)} oldest people")
        
        logger.info(f"Top oldest people per nationality query completed, found {len(result_dict)} nationalities")
        logger.info(f"Results: {result_dict}")
        
        return result_dict
        
    except Exception as e:
        logger.error(f"Error in get_top_oldest_people_per_nationality: {str(e)}")
        raise