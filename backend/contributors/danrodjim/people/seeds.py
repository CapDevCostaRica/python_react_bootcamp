import csv
import pandas as pd
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from database import get_session
from app.models import Person, Food, Family, Hobby, Study
from pathlib import Path

session = get_session()

def seed_person_table():
    people_data_path = Path(__file__).parent / "seed_files" / "people_data.csv"
    physical_data_path = Path(__file__).parent / "seed_files" / "physical_data.csv"
    person_list_temp = []
    person_list_final = []
    with open(people_data_path, newline="", encoding="utf-8") as people_data:
        r = csv.DictReader(people_data)
        seen_ids = set()
        for row in r:
            id = row.get("id")
            name = row.get("full_name")
            if id and name and id not in seen_ids:
                seen_ids.add(id)
                person_list_temp.append({"id": id, "name": name})
    with open(physical_data_path, newline="", encoding="utf-8") as physical_data:
        r = csv.DictReader(physical_data)
        seen_ids = set()
        for row in r:
            id = row.get("person_id")
            eye_color = row.get("eye_color")
            hair_color = row.get("hair_color")
            age = row.get("age")
            height_cm = row.get("height_cm")
            weight_kg = row.get("weight_kg")
            nationality = row.get("nationality")
            if id and eye_color and hair_color and age and height_cm and weight_kg and nationality and id not in seen_ids:
                seen_ids.add(id)
                person = next(filter(lambda d: d.get("id") == id, person_list_temp), None)
                if person:
                    person_list_final.append(
                        Person(
                            id=id, 
                            name=person.get("name"), 
                            eye_color=eye_color, 
                            hair_color=hair_color, 
                            age=age, height_cm=height_cm, 
                            weight_kg=weight_kg, 
                            nationality=nationality
                        )
                    )
    
    session.add_all(person_list_final)
    session.commit()

def seed_food_table():
    food_data_path = Path(__file__).parent / "seed_files" / "favorite_data.csv"
    list_of_foods = []
    for chunk in pd.read_csv(food_data_path, chunksize=50):
        for _, row in chunk.iterrows():
            list_of_foods.append(
                Food(person_id=row["person_id"], name=row["food"])
            )     
    session.add_all(list_of_foods)

def seed_hobby_table():
    hobbie_data_path = Path(__file__).parent / "seed_files" / "hobbies_data.csv"
    list_of_hobbies = []
    for chunk in pd.read_csv(hobbie_data_path, chunksize=50):
        for _, row in chunk.iterrows():
            list_of_hobbies.append(
                Hobby(person_id=row["person_id"], name=row["hobby"])
            )     
    session.add_all(list_of_hobbies)

def seed_family_table():
    family_data_path = Path(__file__).parent / "seed_files" / "family_data.csv"
    family_list = []
    for chunk in pd.read_csv(family_data_path, chunksize=50):
        for _, row in chunk.iterrows():
            family_list.append(
                Family(person_id=row["person_id"], name=row["name"], relation=row["relation"])
            )     
    session.add_all(family_list)

def seed_study_table():
    studies_data_path = Path(__file__).parent / "seed_files" / "studies_data.csv"
    list_of_studies = []
    for chunk in pd.read_csv(studies_data_path, chunksize=50):
        for _, row in chunk.iterrows():
            list_of_studies.append(
                Study(person_id=row["person_id"], degree=row["degree"], institution=row["institution"])
            )     
    session.add_all(list_of_studies)

if __name__ == "__main__":
    session.query(Study).delete()
    session.query(Hobby).delete()
    session.query(Family).delete()
    session.query(Food).delete()
    session.query(Person).delete()
    session.commit()
    seed_person_table()
    seed_food_table()
    seed_hobby_table()
    seed_family_table()
    seed_study_table()
    session.commit()
    session.close()
