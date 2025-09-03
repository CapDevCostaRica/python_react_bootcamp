
import os
import sys
import logging
from flask import request
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, exists

sys.path.append(os.path.dirname(__file__))
from models import Person, PhysicalProfile, FavoriteFood, Hobby, FamilyRelation, Study

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_people(session: Session):

    logger.info("Starting find_people function")
    
    try:
        filters = _parse_filters()
        logger.info(f"Parsed filters: {filters}")
        
        people = _query_people_with_filters(session, filters)
        logger.info(f"Found {len(people)} people matching filters")
        
        return people
        
    except Exception as e:
        logger.error(f"Error in find_people: {str(e)}", exc_info=True)
        raise


def _parse_filters() -> Dict[str, Any]:
    logger.info("Parsing filters from request args")
    filters = {}
    
    logger.info(f"Request args: {dict(request.args)}")
    
    for key, value in request.args.items():
        if key.startswith('filters[') and key.endswith(']'):
            filter_name = key[8:-1] 
            logger.info(f"Processing filter: {filter_name} = {value}")
            
            if filter_name in ['age', 'height_cm', 'weight_kg']:
                try:
                    filters[filter_name] = int(value)
                    logger.info(f"Converted {filter_name} to int: {filters[filter_name]}")
                except ValueError:
                    logger.warning(f"Invalid numeric value for {filter_name}: {value}")
                    continue
            else:
                filters[filter_name] = value
                logger.info(f"Added string filter {filter_name}: {value}")
    
    logger.info(f"Final parsed filters: {filters}")
    return filters

def _query_people_with_filters(session, filters: Dict[str, Any]) -> List[Person]:
    logger.info(f"Starting query with filters: {filters}")
    
    if not filters:
        # If no filters, return all people
        logger.info("No filters provided, returning all people")
        people = session.query(Person).all()
        logger.info(f"Found {len(people)} people (no filters)")
        return people
    
    query = session.query(Person)
    logger.info("Starting with base Person query")
    
    physical_filters = ['eye_color', 'hair_color', 'age', 'height_cm', 'weight_kg', 'nationality']
    physical_filters_present = [key for key in physical_filters if key in filters]
    
    if physical_filters_present:
        logger.info(f"Applying physical profile filters: {physical_filters_present}")
        query = query.join(PhysicalProfile, Person.id == PhysicalProfile.person_id)
        
        if 'eye_color' in filters:
            query = query.filter(PhysicalProfile.eye_color == filters['eye_color'])
            logger.info(f"Added eye_color filter: {filters['eye_color']}")
        if 'hair_color' in filters:
            query = query.filter(PhysicalProfile.hair_color == filters['hair_color'])
            logger.info(f"Added hair_color filter: {filters['hair_color']}")
        if 'age' in filters:
            query = query.filter(PhysicalProfile.age == filters['age'])
            logger.info(f"Added age filter: {filters['age']}")
        if 'height_cm' in filters:
            query = query.filter(PhysicalProfile.height_cm == filters['height_cm'])
            logger.info(f"Added height_cm filter: {filters['height_cm']}")
        if 'weight_kg' in filters:
            query = query.filter(PhysicalProfile.weight_kg == filters['weight_kg'])
            logger.info(f"Added weight_kg filter: {filters['weight_kg']}")
        if 'nationality' in filters:
            query = query.filter(PhysicalProfile.nationality == filters['nationality'])
            logger.info(f"Added nationality filter: {filters['nationality']}")
    
    if 'food' in filters:
        logger.info(f"Adding food filter: {filters['food']}")
        query = query.filter(
            exists().where(
                and_(
                    FavoriteFood.person_id == Person.id,
                    FavoriteFood.food == filters['food']
                )
            )
        )
    
    if 'hobby' in filters:
        logger.info(f"Adding hobby filter: {filters['hobby']}")
        query = query.filter(
            exists().where(
                and_(
                    Hobby.person_id == Person.id,
                    Hobby.hobby == filters['hobby']
                )
            )
        )
    
    if 'family' in filters:
        logger.info(f"Adding family filter: {filters['family']}")
        query = query.filter(
            exists().where(
                and_(
                    FamilyRelation.person_id == Person.id,
                    FamilyRelation.relation == filters['family']
                )
            )
        )
    
    if 'degree' in filters:
        logger.info(f"Adding degree filter: {filters['degree']}")
        query = query.filter(
            exists().where(
                and_(
                    Study.person_id == Person.id,
                    Study.degree == filters['degree']
                )
            )
        )
    
    if 'institution' in filters:
        logger.info(f"Adding institution filter: {filters['institution']}")
        query = query.filter(
            exists().where(
                and_(
                    Study.person_id == Person.id,
                    Study.institution == filters['institution']
                )
            )
        )
    
    logger.info("Executing final query")
    people = query.all()
    logger.info(f"Query executed successfully, found {len(people)} people")
    
    return people