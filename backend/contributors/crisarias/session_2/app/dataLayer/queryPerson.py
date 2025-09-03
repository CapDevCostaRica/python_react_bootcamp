import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../framework')))
from database import get_session
from ..models import Family, FavoriteFood, Hobby, Person, Study
from ..telemetry import logger

def closeSession(session):
    if session:
        session.close()

def getPersonsDL(filter_dict):
    session = None
    try:
        session = get_session()
        query = session.query(Person.full_name)

        # Person fields
        person_fields = ['id', 'full_name', 'eye_color', 'hair_color', 'age', 'height_cm', 'weight_kg', 'nationality']
        for f in person_fields:
            if f in filter_dict:
                value = filter_dict[f]
                if f in ['id', 'age', 'height_cm', 'weight_kg']:
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                query = query.filter(getattr(Person, f) == value)

        # Join and filter related tables
        if 'food' in filter_dict:
            query = query.join(FavoriteFood).filter(FavoriteFood.food == filter_dict['food'])
        if 'hobby' in filter_dict:
            query = query.join(Hobby).filter(Hobby.hobby == filter_dict['hobby'])
        if 'family' in filter_dict:
            query = query.join(Family).filter(Family.relation == filter_dict['family'])
        if 'degree' in filter_dict:
            query = query.join(Study).filter(Study.degree == filter_dict['degree'])
        if 'institution' in filter_dict:
            query = query.join(Study).filter(Study.institution == filter_dict['institution'])

        people = query.all()
        logger.info(f"Retrieved {len(people)} rows for model {Person.__name__}")
        result = []
        for p in people:
            result.append(p[0])
        return result
    except Exception as e:
        logger.error(f"Error retrieving cached resources for model {Person.__name__}: {e}")
        raise e
    finally:
        closeSession(session)