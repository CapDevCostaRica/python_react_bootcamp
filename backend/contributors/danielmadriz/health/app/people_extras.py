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