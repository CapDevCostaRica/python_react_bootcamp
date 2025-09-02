from database import get_session
from sqlalchemy import select, func
from app.models import Person, Food, Family, Hobby, Study

def find_person(filters):
    with get_session() as session:
        person_query = select(Person)

        person_filters = {
            "name": Person.name,
            "eye_color": Person.eye_color,
            "hair_color": Person.hair_color,
            "age": Person.age,
            "height_cm": Person.height_cm,
            "weight_kg": Person.weight_kg,
            "nationality": Person.nationality,
        }

        for key, column in person_filters.items():
            if key in filters:
                person_query = person_query.where(column == filters[key])

        joins = {
            "food": (Food, Food.name),
            "hobby": (Hobby, Hobby.name),
            "family": (Family, Family.relation),
            "degree": (Study, Study.degree),
            "institution": (Study, Study.institution),
        }

        joined_models = set()

        for key, (model, column) in joins.items():
            if key in filters:
                if model not in joined_models:
                    person_query = person_query.join(model)
                    joined_models.add(model)
                person_query = person_query.where(column == filters[key])

        result = session.scalars(person_query).all()

    return result


def find_sushi_ramen_people():
    session = get_session()
    person_query = (
        select(Person)
        .join(Person.foods)
        .where(Food.name.in_(["Sushi", "Ramen"]))
        .group_by(Person.id)
        .having(func.count(func.distinct(Food.name)) == 2)
    )
    results = session.scalars(person_query).all()
    return results