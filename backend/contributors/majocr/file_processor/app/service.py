from collections import defaultdict
from sqlalchemy import String, and_, desc, func
from app.models import Family_majocr, Food_majocr, Hobby_majocr, People_majocr, Person_Food_Association_majocr, Person_Hobby_Association_majocr, Study_majocr

def query_people_by_filters(session, filters):
    print(f"Querying with filters.")
    query = session.query(People_majocr).distinct()

    query = query.join(People_majocr.foods).join(Person_Food_Association_majocr.food)
    query = query.join(People_majocr.hobbies).join(Person_Hobby_Association_majocr.hobby)
    query = query.join(People_majocr.family)
    query = query.join(People_majocr.studies)

    if 'eye_color' in filters:
        query = query.filter(People_majocr.eye_color == filters['eye_color'])
    if 'hair_color' in filters:
        query = query.filter(People_majocr.hair_color == filters['hair_color'])
    if 'age' in filters:
        query = query.filter(People_majocr.age == filters['age'])
    if 'height_cm' in filters:
        query = query.filter(People_majocr.height_cm == filters['height_cm'])
    if 'weight_kg' in filters:
        query = query.filter(People_majocr.weight_kg == filters['weight_kg'])
    if 'nationality' in filters:
        query = query.filter(People_majocr.nationality == filters['nationality'])

    if 'food' in filters:
        query = query.filter(Food_majocr.name.ilike(filters['food']))
    if 'hobby' in filters:
        query = query.filter(Hobby_majocr.name.ilike(filters['hobby']))
    if 'family' in filters:
        query = query.filter(Family_majocr.relation.ilike(filters['family']))
    if 'degree' in filters:
        query = query.filter(Study_majocr.degree.ilike(filters['degree']))
    if 'institution' in filters:
        query = query.filter(Study_majocr.institution.ilike(filters['institution']))

    return query.all()


#Extra 1
#People who like both sushi and ramen
def get_people_like_shushi_and_ramen(session) -> int:
    try:
        sushi_subq = session.query(Person_Food_Association_majocr.person_id).join(Food_majocr).filter(
            Food_majocr.name.ilike("sushi")
        ).subquery()

        ramen_subq = session.query(Person_Food_Association_majocr.person_id).join(Food_majocr).filter(
            Food_majocr.name.ilike("ramen")
        ).subquery()

        count = session.query(People_majocr).filter(
            People_majocr.id.in_(sushi_subq)
        ).filter(
            People_majocr.id.in_(ramen_subq)
        ).count()
        return count
    except Exception as error:
        print(f"Error query sushi and ramen. Error: {error}")

#Extra 2
#People with average weight above 70 grouped by hair color
def get_avg_weight_above_70_by_hair(session):
    try:
        results = (
            session.query(
                People_majocr.hair_color,
                func.avg(People_majocr.weight_kg).label("avg_weight")
            )
            .filter(People_majocr.weight_kg.isnot(None))
            .group_by(People_majocr.hair_color)
            .having(func.avg(People_majocr.weight_kg) > 70)
            .order_by(func.avg(People_majocr.weight_kg).desc())
            .all()
        )

        return {
            hair: round(float(avg_weight), 2)
            for hair, avg_weight in results
            if hair is not None and avg_weight is not None
        }

    except Exception as error:
        print(f"Error query average weight above 70 grouped by hair color. Error: {error}")

#Extra 3
#Most common food overall
def get_most_common_food(session):
    try:
        result = (
            session.query(
                Food_majocr.name,
                func.count(Person_Food_Association_majocr.id).label("food_count")
            )
            .join(Person_Food_Association_majocr, Food_majocr.id == Person_Food_Association_majocr.food_id)
            .group_by(Food_majocr.name)
            .order_by(func.count(Person_Food_Association_majocr.id).desc())
            .limit(1)
            .first()
        )
        return {
            "success": True,
            "data": result[0] if result else None
        }

    except Exception as error:
        print(f"Error query most common food overall. Error: {error}")

def get_avg_weight_by_nationality_and_hair(session):
    #Extra 4
    #Average weight grouped by nationality and hair color
    try:
        results = (
            session.query(
                People_majocr.nationality,
                People_majocr.hair_color,
                func.avg(People_majocr.weight_kg).label("avg_weight")
            )
            .group_by(People_majocr.nationality, People_majocr.hair_color)
            .all()
        )
        print(results)
        data = {
            f"{nationality.lower()}-{hair_color.lower()}": round(avg_weight, 2)
            for nationality, hair_color, avg_weight in results
        }

        return {"success": True, "data": data}

    except Exception as error:
        print(f"Error query average weight grouped by nationality and hair color. Error: {error}")

#Extra 5
#The top 2 oldest people per nationality
def get_top_oldest_natuinality(session):
    try:
        results = (
            session.query(People_majocr.nationality, People_majocr.name, People_majocr.age)
            .order_by(People_majocr.nationality, desc(People_majocr.age))
            .all()
        )
        result = defaultdict(list)
        for person in results:
            key = person.nationality
            if len(result[key]) < 2:
                result[key].append(person.name)
        return dict(result)
    except Exception as error:
        print(f"Error query the top 2 oldest people per nationality. Error: {error}")

#Extra 6
#People ranked by how many hobbies they have (Top 3)
def top_hobbies(session):
    try:
        top_people = (
            session.query(People_majocr.name)
            .join(Person_Hobby_Association_majocr, People_majocr.id == Person_Hobby_Association_majocr.person_id)
            .group_by(People_majocr.id)
            .order_by(func.count(Person_Hobby_Association_majocr.hobby_id).desc(),
                      People_majocr.name.asc())
            .limit(3)
            .all()
        )
        names = [p.name for p in top_people]
        return ({"success": True, "data": names})
    except Exception as error:
        print(f"Error query the top 3 how many hobbies they have . Error: {error}")

#Extra 7
#Average height by nationality and average in general
def avg_height_nationality_general(session):
    try:
        general_avg = (
            session.query(func.avg(People_majocr.height_cm)).scalar()
        )

        nationality_avgs = (
            session.query(
                People_majocr.nationality,
                func.avg(People_majocr.height_cm)
            )
            .group_by(People_majocr.nationality)
            .all()
        )

        nationality_dict = {}
        for nationality, avg in nationality_avgs:
            key = nationality.lower()
            value = round(avg, 2) if avg is not None else 0
            nationality_dict[key] = value


        return {
            "success": True,
            "data": {
                "general": round(general_avg, 2) if general_avg is not None else 0,
                "nationalities": nationality_dict
            }
        }
    except Exception as error:
        print(f"Error query average height by nationality and average in general. Error: {error}")
