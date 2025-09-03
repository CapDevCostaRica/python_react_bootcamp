
import os
import sys
from flask import request
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, exists

# Add the app directory to the path to import models


from models import Person, PhysicalProfile, FavoriteFood, Hobby, FamilyRelation, Study


def find_people(session: Session):
    
    filters = _parse_filters()
    
    people = _query_people_with_filters(session, filters)
    
    return people


def _parse_filters() -> Dict[str, Any]:

    filters = {}
    
    for key, value in request.args.items():
        if key.startswith('filters[') and key.endswith(']'):
            filter_name = key[8:-1]  # Extract filter name from 'filters[key]'
            
            # Convert numeric values
            if filter_name in ['age', 'height_cm', 'weight_kg']:
                try:
                    filters[filter_name] = int(value)
                except ValueError:
                    # Skip invalid numeric values
                    continue
            else:
                filters[filter_name] = value
    
    return filters



def _query_people_with_filters(session, filters: Dict[str, Any]) -> List[Person]:
    """
    Query people records based on filters.
    
    Args:
        session: Database session
        filters: Dictionary of filters
        
    Returns:
        List of Person objects matching the filters
    """
    if not filters:
        # If no filters, return all people
        return session.query(Person).all()
    
    # Start with base query
    query = session.query(Person)
    
    # Apply physical profile filters (direct join since it's 1:1)
    physical_filters = ['eye_color', 'hair_color', 'age', 'height_cm', 'weight_kg', 'nationality']
    if any(key in filters for key in physical_filters):
        query = query.join(PhysicalProfile, Person.id == PhysicalProfile.person_id)
        
        if 'eye_color' in filters:
            query = query.filter(PhysicalProfile.eye_color == filters['eye_color'])
        if 'hair_color' in filters:
            query = query.filter(PhysicalProfile.hair_color == filters['hair_color'])
        if 'age' in filters:
            query = query.filter(PhysicalProfile.age == filters['age'])
        if 'height_cm' in filters:
            query = query.filter(PhysicalProfile.height_cm == filters['height_cm'])
        if 'weight_kg' in filters:
            query = query.filter(PhysicalProfile.weight_kg == filters['weight_kg'])
        if 'nationality' in filters:
            query = query.filter(PhysicalProfile.nationality == filters['nationality'])
    
    # Apply relationship filters using EXISTS subqueries
    if 'food' in filters:
        query = query.filter(
            exists().where(
                and_(
                    FavoriteFood.person_id == Person.id,
                    FavoriteFood.food == filters['food']
                )
            )
        )
    
    if 'hobby' in filters:
        query = query.filter(
            exists().where(
                and_(
                    Hobby.person_id == Person.id,
                    Hobby.hobby == filters['hobby']
                )
            )
        )
    
    if 'family' in filters:
        query = query.filter(
            exists().where(
                and_(
                    FamilyRelation.person_id == Person.id,
                    FamilyRelation.relation == filters['family']
                )
            )
        )
    
    if 'degree' in filters:
        query = query.filter(
            exists().where(
                and_(
                    Study.person_id == Person.id,
                    Study.degree == filters['degree']
                )
            )
        )
    
    if 'institution' in filters:
        query = query.filter(
            exists().where(
                and_(
                    Study.person_id == Person.id,
                    Study.institution == filters['institution']
                )
            )
        )
    
    return query.all()