from app.models import Person, Study, Family, FavoriteFood, Hobby
from app.telemetry import logger
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from database import get_session
import pandas as pd

def seed_people():
    logger.info("Seeding people...")
    session = get_session()
    try:
        logger.info("Getting information from file files/people_data.csv")
        existentIds = {person.id for person in session.query(Person).all()}
        for chunk in pd.read_csv("files/people_data.csv", chunksize=1000):
            for _, row in chunk.iterrows():
                if row["id"] not in existentIds:
                    person = Person(
                        id=row["id"],
                        full_name=row["full_name"]
                    )
                    session.add(person)
                else:
                    logger.info(f"Person with id {row['id']} already exists. Skipping.")
        session.commit()
        logger.info("People seeded successfully.")
    except Exception as e:
        logger.error(f"Error seeding people: {e}")
        session.rollback()
    finally:
        session.close()

def seed_people_physical_data():
    logger.info("Seeding people physical data...")
    session = get_session()
    try:
        logger.info("Getting information from file files/physical_data.csv")
        existentIds = {person.id for person in session.query(Person).all()}
        for chunk in pd.read_csv("files/physical_data.csv", chunksize=1000):
            for _, row in chunk.iterrows():
                if row["person_id"] in existentIds:
                    person = Person(id=row["person_id"])
                    person.eye_color = row["eye_color"]
                    person.hair_color = row["hair_color"]
                    person.age = row["age"]
                    person.height_cm = row["height_cm"]
                    person.weight_kg = row["weight_kg"]
                    person.nationality = row["nationality"]
                    session.merge(person)
        session.commit()
        logger.info("People data seeded successfully.")
    except Exception as e:
        logger.error(f"Error seeding people data: {e}")
        session.rollback()
    finally:
        session.close()

def seed_hobbies():
    logger.info("Seeding hobbies...")
    session = get_session()
    try:
        logger.info("Getting information from file files/hobbies_data.csv")
        for chunk in pd.read_csv("files/hobbies_data.csv", chunksize=1000):
            for _, row in chunk.iterrows():
                existing_hobbies = {hobby.hobby for hobby in session.query(Hobby).filter(Hobby.person_id == row["person_id"]).all()}
                if row["hobby"] not in existing_hobbies:
                    hobby = Hobby(person_id=row["person_id"], hobby=row["hobby"])
                    session.add(hobby)
                else:
                    logger.info(f"Hobby {row['hobby']} for person_id {row['person_id']} already exists. Skipping.")
        session.commit()
        logger.info("Hobbies seeded successfully.")
    except Exception as e:
        logger.error(f"Error seeding hobbies: {e}")
        session.rollback()
    finally:
        session.close()

def seed_favorite_foods():
    logger.info("Seeding favorite foods...")
    session = get_session()
    try:
        logger.info("Getting information from file files/favorite_data.csv")
        for chunk in pd.read_csv("files/favorite_data.csv", chunksize=1000):
            for _, row in chunk.iterrows():
                existing_favorite_foods = {food.food for food in session.query(FavoriteFood).filter(FavoriteFood.person_id == row["person_id"]).all()}
                if row["food"] not in existing_favorite_foods:
                    favorite_food = FavoriteFood(person_id=row["person_id"], food=row["food"])
                    session.add(favorite_food)
                else:
                    logger.info(f"Favorite food {row['food']} for person_id {row['person_id']} already exists. Skipping.")
        session.commit()
        logger.info("Favorite foods seeded successfully.")
    except Exception as e:
        logger.error(f"Error seeding favorite foods: {e}")
        session.rollback()
    finally:
        session.close()

def seed_studies():
    logger.info("Seeding studies...")
    session = get_session()
    try:
        logger.info("Getting information from file files/studies_data.csv")
        for chunk in pd.read_csv("files/studies_data.csv", chunksize=1000):
            for _, row in chunk.iterrows():
                existing_studies = {(study.degree, study.institution) for study in session.query(Study).filter(Study.person_id == row["person_id"]).all()}
                if (row["degree"], row["institution"]) not in existing_studies:
                    study = Study(person_id=row["person_id"], degree=row["degree"], institution=row["institution"])
                    session.add(study)
                else:
                    logger.info(f"Study {row['degree']} at {row['institution']} for person_id {row['person_id']} already exists. Skipping.")
        session.commit()
        logger.info("Studies seeded successfully.")
    except Exception as e:
        logger.error(f"Error seeding studies: {e}")
        session.rollback()
    finally:
        session.close()

def seed_families():
    logger.info("Seeding families...")
    session = get_session()
    try:
        logger.info("Getting information from file files/family_data.csv")
        for chunk in pd.read_csv("files/family_data.csv", chunksize=1000):
            for _, row in chunk.iterrows():
                existing_families = {(family.relation, family.name) for family in session.query(Family).filter(Family.person_id == row["person_id"]).all()}
                if (row["relation"], row["name"]) not in existing_families:
                    family = Family(person_id=row["person_id"], relation=row["relation"], name=row["name"])
                    session.add(family)
                else:
                    logger.info(f"Family relation {row['relation']} with name {row['name']} for person_id {row['person_id']} already exists. Skipping.")
        session.commit()
        logger.info("Families seeded successfully.")
    except Exception as e:
        logger.error(f"Error seeding families: {e}")
        session.rollback()
    finally:
        session.close()

def seed_all_data():
    seed_people()
    seed_people_physical_data()
    seed_hobbies()
    seed_favorite_foods()
    seed_studies()
    seed_families()

if __name__ == "__main__":
    seed_all_data()
