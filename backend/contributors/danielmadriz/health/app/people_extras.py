import logging
import sys
import os
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, exists
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)
from models import Person, FavoriteFood

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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