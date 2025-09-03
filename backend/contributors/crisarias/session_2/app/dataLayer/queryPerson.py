import os
import sys

from sqlalchemy import func, desc, distinct
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../framework')))
from database import get_session
from ..models import Family, FavoriteFood, Hobby, Person, Study
from ..telemetry import logger

def closeSession(session):
    if session:
        session.close()

def buildPersonList(people):
        logger.info(f"Retrieved {len(people)} rows for model {Person.__name__}")
        result = []
        for p in people:
            result.append(p[0])
        return result

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

        people = query.distinct().all()
        return buildPersonList(people)
    except Exception as e:
        logger.error(f"Error retrieving cached resources for model {Person.__name__}: {e}")
        raise e
    finally:
        closeSession(session)

def getPersonThatEatFoodsDL(foods):
    session = None
    try:
        session = get_session()
        # Get people who eat ALL the foods (exclusive)
        expected_count = len(set(foods))
        query = (
            session.query(Person.id)
            .join(FavoriteFood)
            .filter(FavoriteFood.food.in_(foods))
            .group_by(Person.id)
            .having(func.count(distinct(FavoriteFood.food)) == expected_count)
        )
        count = query.count()
        logger.info(f"Retrieved count: {count}")        
        return count
    except Exception as e:
        logger.error(f"Error retrieving cached resources for model {Person.__name__}: {e}")
        raise e
    finally:
        closeSession(session)

def getAverageWeightAbove70ByHairDL():
    session = None
    try:
        session = get_session()
        query = session.query(
            Person.hair_color,
            func.avg(Person.weight_kg).label('avg_weight')
        ).group_by(Person.hair_color).having(func.avg(Person.weight_kg) > 70)
        results = query.all()
        logger.info(f"Retrieved {len(results)} hair colors with average weight above 70")
        
        data = {}
        for hair_color, avg_weight in results:
            data[hair_color] = round(float(avg_weight), 2) if avg_weight else 0
        
        return data
    except Exception as e:
        logger.error(f"Error retrieving average weight above 70 by hair color: {e}")
        raise e
    finally:
        closeSession(session)

def getMostCommonFoodDL():
    session = None
    try:
        session = get_session()
        query = session.query(FavoriteFood.food, func.count(FavoriteFood.food)).group_by(FavoriteFood.food).order_by(func.count(FavoriteFood.food).desc()).limit(1)        
        foods = query.all()
        logger.info(f"Retrieved {len(foods)} rows for model {FavoriteFood.__name__}")
        if not foods:
            return []
        return [f[0] for f in foods]
    except Exception as e:
        logger.error(f"Error retrieving cached resources for model {FavoriteFood.__name__}: {e}")
        raise e
    finally:
        closeSession(session)

def getAverageWeightByNationalityAndHairDL():
    session = None
    try:
        session = get_session()
        query = session.query(
            Person.nationality,
            Person.hair_color,
            func.avg(Person.weight_kg)
        ).group_by(Person.nationality, Person.hair_color)        
        
        results = query.all()
        logger.info(f"Retrieved {len(results)} rows for average weight by nationality and hair color")
        
        data = {}
        for nationality, hair_color, avg_weight in results:
            key = f"{nationality}-{hair_color}"
            rounded_weight = round(float(avg_weight), 2) if avg_weight else 0
            data[key] = int(rounded_weight) if rounded_weight == int(rounded_weight) else rounded_weight
        
        return data
    except Exception as e:
        logger.error(f"Error retrieving average weight by nationality and hair color: {e}")
        raise e
    finally:
        closeSession(session)

def getTopOldestByNationalityDL():
    session = None
    try:
        session = get_session()
        # Use window function in subquery, do not add column to model
        subq = (
            session.query(
            Person.nationality,
            Person.full_name,
            func.row_number().over(
                partition_by=Person.nationality,
                order_by=[Person.age.desc(), Person.full_name]
            ).label('rnk')
            )
        ).subquery()

        # Select only top 2 oldest per nationality
        query = session.query(subq.c.nationality, subq.c.full_name).filter(subq.c.rnk <= 2)        
        results = query.all()

        # Group results by nationality
        data = {}
        for nationality, full_name in results:
            key = nationality.lower() if nationality else ''
            if key not in data:
                data[key] = []
            data[key].append(full_name)

        logger.info(f"Retrieved top 2 oldest people for {len(data)} nationalities using window function")
        return data
    except Exception as e:
        logger.error(f"Error retrieving top oldest people by nationality: {e}")
        raise e
    finally:
        closeSession(session)

def getTopPeopleByHobbiesCountDL():
    session = None
    try:
        session = get_session()
        query = session.query(
            Person.full_name,
            func.count(Hobby.hobby).label('hobby_count')
        ).join(Hobby).group_by(Person.full_name).order_by(desc('hobby_count'), Person.full_name).limit(3)
        results = query.all()
        return buildPersonList(results)
    except Exception as e:
        logger.error(f"Error retrieving top people by hobby count: {e}")
        raise e
    finally:
        closeSession(session)

def getAverageHeightByNationalityAndGeneralDL():
    session = None
    try:
        session = get_session()
        
        # Get average height by nationality
        nationality_query = session.query(
            Person.nationality,
            func.avg(Person.height_cm)
        ).group_by(Person.nationality)
        
        nationality_results = nationality_query.all()
        
        # Get general average height
        general_query = session.query(func.avg(Person.height_cm))
        general_result = general_query.scalar()
        
        logger.info(f"Retrieved average height for {len(nationality_results)} nationalities and general average")
        
        data = {
            "general": round(float(general_result), 2) if general_result else 0,
            "nationalities": {}
        }
        
        for nationality, avg_height in nationality_results:
            key = nationality.lower() if nationality else 'unknown'
            data["nationalities"][key] = round(float(avg_height), 2) if avg_height else 0

        return data
    except Exception as e:
        logger.error(f"Error retrieving average height by nationality and general: {e}")
        raise e
    finally:
        closeSession(session)
