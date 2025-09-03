from database import get_session
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from app.models import Person, Food, Family, Hobby, Study
import csv
import heapq
from collections import Counter
from pathlib import Path

def find_person(filters):
    with get_session() as session:
        person_query = select(Person).options(
            selectinload(Person.foods),
            selectinload(Person.hobbies),
            selectinload(Person.family),
            selectinload(Person.studies)
        )

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


def find_sushi_ramen():
    with get_session() as session:
        person_query = (
            select(Person)
            .join(Person.foods)
            .where(func.lower(Food.name).in_(["sushi", "ramen"]))
            .group_by(Person.id)
            .having(func.count(func.distinct(func.lower(Food.name))) == 2)
        )
        results = session.scalars(person_query).all()
    return results


def find_avg_weight_above_70_hair():
    with get_session() as session:
        person_query = (
            select(Person.hair_color, func.avg(Person.weight_kg))
            .group_by(Person.hair_color)
            .having(func.avg(Person.weight_kg) > 70)
        )
        results = session.execute(person_query).all()
    return {hair: round(float(avg), 2) for hair, avg in results}

# This next two funtions do the same, they find the most common food. For the exercise I will use the first one, 
# the second it's here just to satisfy my curiosity.
def find_most_common_food():
    with get_session() as session:
        food_query = (
            select(Food.name, func.count().label("most_common"))
            .group_by(Food.name)
            .order_by(desc("most_common"))
            .limit(1)
        )

        result = session.execute(food_query).first()

    return result

# I made this one just to check how the reading files by heaps approach works. 
# Actually, the function was created by Google Search's AI (I was running out of time, sorry). 
# But I looked it up precisely because I remembered that using heaps worked to get top-k values.
# I decided to leave the code here to analyse it and learn how it works. Also, to compare the time of execution with the db approach.
def find_most_common_food_by_file():
    value_counts = Counter()
    column_name = "food"
    file_path = Path(__file__).parent / "seed_files" / "favorite_data.csv"

    try:
        with open(file_path, mode='r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            if column_name not in reader.fieldnames:
                print(f"Error: Column '{column_name}' not found in the CSV file.")
                return None, 0

            for row in reader:
                value_counts[row[column_name]] += 1

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None, 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, 0

    if not value_counts:
        return None, 0

    min_heap = []

    for value, count in value_counts.items():
        if len(min_heap) < 1:
            heapq.heappush(min_heap, (count, value))
        else:
            if count > min_heap[0][0]:
                heapq.heapreplace(min_heap, (count, value))

    if min_heap:
        most_common_count, most_common_val = min_heap[0]
        return most_common_val, most_common_count
    else:
        return None, 0
    

def find_avg_weight_nationality_hair():
    with get_session() as session:
        person_query = (
            select(
                func.lower(Person.nationality),
                Person.hair_color,
                func.avg(Person.weight_kg).label("avg_weight")
            )
            .group_by(Person.nationality, Person.hair_color)
            .order_by(Person.nationality, Person.hair_color)
        )

        result = session.execute(person_query).all()
    return result