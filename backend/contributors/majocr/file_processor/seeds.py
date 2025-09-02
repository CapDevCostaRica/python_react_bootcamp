from collections import defaultdict
import csv
from pathlib import Path
from marshmallow import ValidationError
from app.models import Family_majocr, Food_majocr, Hobby_majocr, People_majocr, Person_Food_Association_majocr, Person_Hobby_Association_majocr, Study_majocr
from app.schema import FamilySchema_majocr, FoodSchema_majocr, HobbySchema_majocr, PeopleSchema_majocr, PersonFoodAssociationSchema_majocr, PersonHobbyAssociationSchema_majocr, StudySchema_majocr

def validate_csv_file(file_path):
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"Not a file: {file_path}")    
    if file_path.stat().st_size == 0:
        raise ValueError(f"File is empty: {file_path}")
    return file_path
    
def load_csv_to_dict(file_path, key_field):
    data = {}
    file_path = validate_csv_file(file_path)
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                key = row[key_field]
                data[key] = row
    except PermissionError:
        raise PermissionError(f"Permission denied when accessing file: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error reading CSV file {file_path}: {e}")
    return data

def load_csv_to_list(file_path, key_field):
    data = defaultdict(list)
    file_path = validate_csv_file(file_path)
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                key = row.get(key_field)
                if key:
                    data[key.strip()].append(row)
    except PermissionError:
        raise PermissionError(f"Permission denied when accessing file: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error reading CSV file {file_path}: {e}")
    return dict(data)

def load_unique_hobbies(hobbies_data):
    unique_hobbies = set()
    for rows in hobbies_data.values():
        for row in rows:
            hobby = row.get('hobby', '').strip().lower()
            if hobby:
                unique_hobbies.add(hobby)
    return unique_hobbies

def insert_new_hobbies(session, unique_hobbies):
    existing_hobbies = {
        hobby.name for hobby in session.query(Hobby_majocr).filter(Hobby_majocr.name.in_(unique_hobbies)).all()
    }

    for hobby_name in unique_hobbies:
        if hobby_name not in existing_hobbies:
            try:
                validate_data = HobbySchema_majocr().load({"name": hobby_name})
                new_hobby = Hobby_majocr(**validate_data)
                session.add(new_hobby)
            except ValidationError as error:
                print(f"Validation error for hobby '{hobby_name}': {error.messages}")
    session.commit()
    print(f"Inserted {len(unique_hobbies)} unique hobbies.")

def link_hobbies_to_people(session, hobbies_data):
    hobby_map = {
        hobby.name: hobby.id for hobby in session.query(Hobby_majocr).all()
    }
    existing_associations = {
        (assoc.person_id, assoc.hobby_id) 
        for assoc in session.query(Person_Hobby_Association_majocr).all()
    }

    new_associations = []
    print(f"Linking hobbies to people...")
    for rows in hobbies_data.values():
        for row in rows:
            try:
                person_id = int(row.get('person_id', '').strip())
            except ValueError:
                print(f"Invalid person_id '{row['person_id']}' in hobbies data.")
                continue

            hobby_name = row.get('hobby', '').strip().lower()
            hobby_id = hobby_map.get(hobby_name)
            
            if not hobby_id:
                print(f"Hobby '{hobby_name}' not found in database.")
                raise ValueError(f"Hobby '{hobby_name}' not found in database.")
                        
            if (person_id, hobby_id) not in existing_associations:
                try:
                    validate_data = PersonHobbyAssociationSchema_majocr().load({
                        "person_id": person_id,
                        "hobby_id": hobby_id
                    })
                    new_association = Person_Hobby_Association_majocr(**validate_data)
                    new_associations.append(new_association)
                except ValidationError as error:
                    print(f"Validation error for person_id {person_id} and hobby_id {hobby_id}: {error.messages}")
            else:
                print(f"Association between person_id {person_id} and hobby_id {hobby_id} already exists.")
    session.add_all(new_associations)
    session.commit()
    print(f"Linked {len(new_associations)} new person-hobby associations.")

def seed_people(session, people_csv_path, physical_csv_path):
    people_data = load_csv_to_dict(people_csv_path, 'id')
    physical_data = load_csv_to_dict(physical_csv_path, 'person_id')

     # Merge physical attributes into people_data   
    for person_id, person_row in people_data.items():
        if person_id not in physical_data:
            print(f"Missing physical data for person_id: {person_id}")
            continue
        
        physical_row = physical_data[person_id]

        merged_row = {
            "id": int(person_id),
            "name": person_row['full_name'],
            "age": int(physical_row['age']),
            "eye_color": physical_row['eye_color'],
            "hair_color": physical_row['hair_color'],
            "height_cm": float(physical_row['height_cm']),
            "weight_kg": float(physical_row['weight_kg']),
            "nationality": physical_row['nationality'] }
        try:
            validated_data = PeopleSchema_majocr().load(merged_row)
            person = People_majocr(**validated_data)
            session.add(person)
        except ValidationError as error:
            print(f"Validation error for person_id {person_id}: {error.messages}")        
    session.commit()

def seed_hobbies(session, hobbies_csv_path):
    hobbies_data = load_csv_to_list(hobbies_csv_path, 'person_id')
    unique_hobbies = load_unique_hobbies(hobbies_data)
    insert_new_hobbies(session, unique_hobbies)
    link_hobbies_to_people(session, hobbies_data)

def load_unique_foods(foods_data):
    unique_foods = set()
    for rows in foods_data.values():
        for row in rows:
            food = row.get('food', '').strip().lower()
            if food:
                unique_foods.add(food)
    return unique_foods

def insert_new_foods(session, unique_foods):
    existing_foods = {
        food.name for food in session.query(Food_majocr).filter(Food_majocr.name.in_(unique_foods)).all()
    }

    for food_name in unique_foods:
        if food_name not in existing_foods:
            try:
                validate_data = FoodSchema_majocr().load({"name": food_name})
                new_food = Food_majocr(**validate_data)
                session.add(new_food)
            except ValidationError as error:
                print(f"Validation error for food '{food_name}': {error.messages}")

    session.commit()
    print(f"Inserted {len(unique_foods)} unique foods.")

def link_foods_to_people(session, foods_data):
    food_map = {
        food.name: food.id for food in session.query(Food_majocr).all()
    }
    existing_associations = {
        (assoc.person_id, assoc.food_id) 
        for assoc in session.query(Person_Food_Association_majocr).all()
    }

    new_associations = []
    print(f"Linking foods to people...")
    for rows in foods_data.values():
        for row in rows:
            try:
                person_id = int(row.get('person_id', '').strip())
            except ValueError:
                print(f"Invalid person_id '{row['person_id']}' in foods data.")
                continue

            food_name = row.get('food', '').strip().lower()
            food_id = food_map.get(food_name)
            
            if not food_id:
                print(f"Food '{food_name}' not found in database.")
                raise ValueError(f"Food '{food_name}' not found in database.")
                        
            if (person_id, food_id) not in existing_associations:
                try:
                    validate_data = PersonFoodAssociationSchema_majocr().load({
                        "person_id": person_id,
                        "food_id": food_id
                    })
                    new_association = Person_Food_Association_majocr(**validate_data)
                    new_associations.append(new_association)

                except ValidationError as error:
                    print(f"Validation error for person_id {person_id} and food_id {food_id}: {error.messages}")
            else:
                print(f"Association between person_id {person_id} and food_id {food_id} already exists.")
    session.add_all(new_associations)
    session.commit()
    print(f"Linked {len(new_associations)} new person-food associations.")

def seed_foods(session, foods_csv_path):
    foods_data = load_csv_to_list(foods_csv_path, 'person_id')
    unique_foods = load_unique_foods(foods_data)
    insert_new_foods(session, unique_foods)
    link_foods_to_people(session, foods_data)  

def seed_family(session, family_csv_path):
    family_data = load_csv_to_list(family_csv_path, 'person_id')
    relationship = set()

    for rows in family_data.values():
        for row in rows:
            person_id = int(row.get('person_id', '').strip())
            relation = row.get('relation', '').strip()
            name = row.get('name', '').strip()

            if (person_id, relation, name) in relationship:
                print(f"Duplicate family relationship for person_id {person_id} and relation {relation} with {name}. Skipping.")
                continue
            relationship.add((person_id, relation, name))
            try:
                validate_data = FamilySchema_majocr().load({
                    "person_id": person_id,
                    "relation": relation,
                    "name": name
                })
                
                family_entry = Family_majocr(
                    **validate_data
                )
                session.add(family_entry)
            except ValidationError as error:
                print(f"Validation error for family relationship person_id {person_id}, relation {relation}, name {name}: {error.messages}")
    session.commit()
    print(f"Inserted {len(relationship)} family relationships.")

def seed_studies(session, studies_csv_path):
    studies_data = load_csv_to_list(studies_csv_path, 'person_id')
    studies_records = set()

    for rows in studies_data.values():
        for row in rows:
            person_id = int(row.get('person_id', '').strip())
            degree = row.get('degree', '').strip()
            institution = row.get('institution', '').strip()
            
            if (person_id, degree, institution) in studies_records:
                print(f"Duplicate study record for person_id {person_id} and degree {degree} at {institution}. Skipping.")
                continue
            
            studies_records.add((person_id, degree, institution))
            try:
                validate_data = StudySchema_majocr().load({
                    "person_id": person_id,
                    "degree": degree,
                    "institution": institution
                })
                study_entry = Study_majocr(
                    **validate_data
                )
                session.add(study_entry)
            except ValidationError as error:
                print(f"Validation error for study record person_id {person_id}, degree {degree}, institution {institution}: {error.messages}")
            
    session.commit()
    print(f"Inserted {len(studies_records)} study records.")   

if __name__ == '__main__':
    from main import is_data_seeded, get_session
    session = get_session()
    is_data_seeded(session)