from sqlalchemy import and_, func, desc
from app.database import get_session
from app.models import (
    RandymoralesPerson,
    RandymoralesPhysicalData,
    RandymoralesFamilyRelation,
    RandymoralesFavoriteFood,
    RandymoralesHobby,
    RandymoralesStudy
)

def find_people_by_filters(filters):
    """
    Find people based on multiple filter criteria

    Args:
        filters (dict): Dictionary containing filter criteria

    Returns:
        tuple: (list of names, total count)
    """
    session = get_session()

    try:
        # Start with base query joining all necessary tables
        query = session.query(RandymoralesPerson).join(
            RandymoralesPhysicalData,
            RandymoralesPerson.id == RandymoralesPhysicalData.person_id
        )

        # Apply physical filters
        if 'eye_color' in filters:
            query = query.filter(RandymoralesPhysicalData.eye_color == filters['eye_color'])

        if 'hair_color' in filters:
            query = query.filter(RandymoralesPhysicalData.hair_color == filters['hair_color'])

        if 'age' in filters:
            query = query.filter(RandymoralesPhysicalData.age == filters['age'])

        if 'height_cm' in filters:
            query = query.filter(RandymoralesPhysicalData.height_cm == filters['height_cm'])

        if 'weight_kg' in filters:
            query = query.filter(RandymoralesPhysicalData.weight_kg == filters['weight_kg'])

        if 'nationality' in filters:
            query = query.filter(RandymoralesPhysicalData.nationality == filters['nationality'])

        # Apply family filter
        if 'family' in filters:
            family_subquery = session.query(RandymoralesFamilyRelation.person_id).filter(
                RandymoralesFamilyRelation.relation == filters['family']
            ).subquery()
            query = query.filter(RandymoralesPerson.id.in_(family_subquery))

        # Apply food filter
        if 'food' in filters:
            food_subquery = session.query(RandymoralesFavoriteFood.person_id).filter(
                RandymoralesFavoriteFood.food == filters['food']
            ).subquery()
            query = query.filter(RandymoralesPerson.id.in_(food_subquery))

        # Apply hobby filter
        if 'hobby' in filters:
            hobby_subquery = session.query(RandymoralesHobby.person_id).filter(
                RandymoralesHobby.hobby == filters['hobby']
            ).subquery()
            query = query.filter(RandymoralesPerson.id.in_(hobby_subquery))

        # Apply education filters
        if 'degree' in filters:
            degree_subquery = session.query(RandymoralesStudy.person_id).filter(
                RandymoralesStudy.degree == filters['degree']
            ).subquery()
            query = query.filter(RandymoralesPerson.id.in_(degree_subquery))

        if 'institution' in filters:
            institution_subquery = session.query(RandymoralesStudy.person_id).filter(
                RandymoralesStudy.institution == filters['institution']
            ).subquery()
            query = query.filter(RandymoralesPerson.id.in_(institution_subquery))

        # Execute query and get results
        people = query.all()

        # Prepare response data
        result_names = [person.full_name for person in people]

        return result_names, len(result_names)

    finally:
        session.close()


# Extra Credit Functions

def get_sushi_ramen_lovers():
    """
    Extra 1: People who like both sushi and ramen
    Returns count of people who like both
    """
    session = get_session()

    try:
        # Find people who like sushi
        sushi_lovers = session.query(RandymoralesFavoriteFood.person_id).filter(
            RandymoralesFavoriteFood.food == 'sushi'
        ).subquery()

        # Find people who like ramen
        ramen_lovers = session.query(RandymoralesFavoriteFood.person_id).filter(
            RandymoralesFavoriteFood.food == 'ramen'
        ).subquery()

        # Find people who like both (intersection)
        both_lovers = session.query(RandymoralesPerson).filter(
            and_(
                RandymoralesPerson.id.in_(sushi_lovers),
                RandymoralesPerson.id.in_(ramen_lovers)
            )
        ).count()

        return both_lovers

    finally:
        session.close()


def get_avg_weight_above_70_by_hair():
    """
    Extra 2: People with average weight above 70 grouped by hair color
    Returns dict with hair colors and their average weights (only if avg > 70)
    """
    session = get_session()

    try:
        # Group by hair color and calculate average weight
        results = session.query(
            RandymoralesPhysicalData.hair_color,
            func.avg(RandymoralesPhysicalData.weight_kg).label('avg_weight')
        ).group_by(
            RandymoralesPhysicalData.hair_color
        ).having(
            func.avg(RandymoralesPhysicalData.weight_kg) > 70
        ).all()

        # Convert to dict with rounded averages
        return {hair_color: round(avg_weight) for hair_color, avg_weight in results}

    finally:
        session.close()


def get_most_common_food():
    """
    Extra 3: Most common food overall
    Returns the food name that appears most frequently
    """
    session = get_session()

    try:
        # Group by food and count occurrences
        result = session.query(
            RandymoralesFavoriteFood.food,
            func.count(RandymoralesFavoriteFood.food).label('food_count')
        ).group_by(
            RandymoralesFavoriteFood.food
        ).order_by(
            desc('food_count')
        ).first()

        return result.food if result else None

    finally:
        session.close()


def get_avg_weight_by_nationality_hair():
    """
    Extra 4: Average weight grouped by nationality and hair color
    Returns dict with "nationality-haircolor" keys and average weight values
    """
    session = get_session()

    try:
        # Group by nationality and hair color, calculate average weight
        results = session.query(
            RandymoralesPhysicalData.nationality,
            RandymoralesPhysicalData.hair_color,
            func.avg(RandymoralesPhysicalData.weight_kg).label('avg_weight')
        ).group_by(
            RandymoralesPhysicalData.nationality,
            RandymoralesPhysicalData.hair_color
        ).all()

        # Convert to dict with "nationality-haircolor" format
        return {
            f"{nationality.lower()}-{hair_color}": round(avg_weight)
            for nationality, hair_color, avg_weight in results
        }

    finally:
        session.close()


def get_top_oldest_by_nationality():
    """
    Extra 5: The top 2 oldest people per nationality
    Returns dict with nationality keys and lists of 2 oldest people names
    """
    session = get_session()

    try:
        # Get all nationalities
        nationalities = session.query(RandymoralesPhysicalData.nationality).distinct().all()

        result = {}

        for (nationality,) in nationalities:
            # Get top 2 oldest people for each nationality
            oldest_people = session.query(
                RandymoralesPerson.full_name
            ).join(
                RandymoralesPhysicalData,
                RandymoralesPerson.id == RandymoralesPhysicalData.person_id
            ).filter(
                RandymoralesPhysicalData.nationality == nationality
            ).order_by(
                desc(RandymoralesPhysicalData.age)
            ).limit(2).all()

            result[nationality.lower()] = [name for (name,) in oldest_people]

        return result

    finally:
        session.close()


def get_top_people_by_hobbies():
    """
    Extra 6: People ranked by how many hobbies they have (Top 3)
    Returns list of top 3 people names with most hobbies
    """
    session = get_session()

    try:
        # Count hobbies per person and get top 3
        results = session.query(
            RandymoralesPerson.full_name,
            func.count(RandymoralesHobby.hobby).label('hobby_count')
        ).join(
            RandymoralesHobby,
            RandymoralesPerson.id == RandymoralesHobby.person_id
        ).group_by(
            RandymoralesPerson.id,
            RandymoralesPerson.full_name
        ).order_by(
            desc('hobby_count')
        ).limit(3).all()

        return [name for name, count in results]

    finally:
        session.close()


def get_avg_height_by_nationality_and_general():
    """
    Extra 7: Average height by nationality and average in general
    Returns dict with general average and nationalities breakdown
    """
    session = get_session()

    try:
        # Get general average height
        general_avg = session.query(
            func.avg(RandymoralesPhysicalData.height_cm)
        ).scalar()

        # Get average height by nationality
        nationality_results = session.query(
            RandymoralesPhysicalData.nationality,
            func.avg(RandymoralesPhysicalData.height_cm).label('avg_height')
        ).group_by(
            RandymoralesPhysicalData.nationality
        ).all()

        # Build response
        nationalities = {
            nationality.lower(): round(avg_height)
            for nationality, avg_height in nationality_results
        }

        return {
            "general": round(general_avg) if general_avg else 0,
            "nationalities": nationalities
        }

    finally:
        session.close()
