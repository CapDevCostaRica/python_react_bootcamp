from app.models import Family_majocr, Food_majocr, Hobby_majocr, People_majocr, Person_Food_Association_majocr, Person_Hobby_Association_majocr, Study_majocr
from seeds import seed_family, seed_foods, seed_hobbies, seed_people, seed_studies

def actual_validation_count(session, table, min_expected):
    actual_count = session.query(table).count()
    if actual_count == 0:
        print(f"No entries found in the {table.__tablename__} table.")
        return False
    elif actual_count < min_expected:
        print(f"Only {actual_count} entries found in the {table.__tablename__} table, which is less than the expected minimum of {min_expected}.")
        return False
    else:
        print(f"{actual_count} entries found in the {table.__tablename__} table.")
        return True

def is_people_seeded(session):
    return actual_validation_count(session, People_majocr, 100)

def is_family_seeded(session):
    return actual_validation_count(session, Family_majocr, 241)

def is_studies_seeded(session):
    return actual_validation_count(session, Study_majocr, 153)

def is_hobbies_seeded(session):
    hobbies_exist = actual_validation_count(session, Hobby_majocr, 8)
    associations = actual_validation_count(session, Person_Hobby_Association_majocr, 300)
    return hobbies_exist and associations

def is_foods_seeded(session):
    foods_exist = actual_validation_count(session, Food_majocr, 8)
    associations = actual_validation_count(session, Person_Food_Association_majocr, 200)
    return foods_exist and associations



def get_seed_config(csv_paths):
    return {
        "People_majocr": {
            "check": is_people_seeded,
            "seed": seed_people,
            "args": [csv_paths["people"], csv_paths["physical"]]
        },
        "Hobby_majocr": {
            "check": is_hobbies_seeded,
            "seed": seed_hobbies,
            "args": [csv_paths["hobbies"]]
        },
        "Food_majocr": {
            "check": is_foods_seeded,
            "seed": seed_foods,
            "args": [csv_paths["foods"]]
        },
        "Family_majocr": {
            "check": is_family_seeded,
            "seed": seed_family,
            "args": [csv_paths["family"]]
        },
        "Study_majocr": {
            "check": is_studies_seeded,
            "seed": seed_studies,
            "args": [csv_paths["studies"]]
        }
    }
