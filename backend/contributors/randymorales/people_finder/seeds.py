import csv
from app.database import get_session
from app.models import (
    RandymoralesPerson,
    RandymoralesPhysicalData,
    RandymoralesFamilyRelation,
    RandymoralesFavoriteFood,
    RandymoralesHobby,
    RandymoralesStudy
)

def seed_people_data():
    """Seed all people-related data from CSV files"""
    session = get_session()

    try:
        # Check if data already exists to avoid duplicates
        if session.query(RandymoralesPerson).count() > 0:
            print("People data already seeded. Skipping...")
            return

        # Path to CSV files
        csv_path = "/app/contributors/randymorales/people_finder/data"

        # Seed people first (main table)
        print("Seeding people...")
        with open(f"{csv_path}/people_data.csv", 'r') as file:
            reader = csv.DictReader(file)
            people_batch = []
            for row in reader:
                person = RandymoralesPerson(
                    id=int(row['id']),
                    full_name=row['full_name']
                )
                people_batch.append(person)

            session.add_all(people_batch)
            session.flush()  # Flush to ensure IDs are available

        # Seed physical data
        print("Seeding physical data...")
        with open(f"{csv_path}/physical_data.csv", 'r') as file:
            reader = csv.DictReader(file)
            physical_batch = []
            for row in reader:
                physical_data = RandymoralesPhysicalData(
                    person_id=int(row['person_id']),
                    eye_color=row['eye_color'],
                    hair_color=row['hair_color'],
                    age=int(row['age']),
                    height_cm=int(row['height_cm']),
                    weight_kg=int(row['weight_kg']),
                    nationality=row['nationality']
                )
                physical_batch.append(physical_data)

            session.add_all(physical_batch)

        # Seed family relations
        print("Seeding family relations...")
        with open(f"{csv_path}/family_data.csv", 'r') as file:
            reader = csv.DictReader(file)
            family_batch = []
            for row in reader:
                family_relation = RandymoralesFamilyRelation(
                    person_id=int(row['person_id']),
                    relation=row['relation'],
                    name=row['name']
                )
                family_batch.append(family_relation)

            session.add_all(family_batch)

        # Seed favorite foods
        print("Seeding favorite foods...")
        with open(f"{csv_path}/favorite_data.csv", 'r') as file:
            reader = csv.DictReader(file)
            foods_batch = []
            for row in reader:
                favorite_food = RandymoralesFavoriteFood(
                    person_id=int(row['person_id']),
                    food=row['food']
                )
                foods_batch.append(favorite_food)

            session.add_all(foods_batch)

        # Seed hobbies
        print("Seeding hobbies...")
        with open(f"{csv_path}/hobbies_data.csv", 'r') as file:
            reader = csv.DictReader(file)
            hobbies_batch = []
            for row in reader:
                hobby = RandymoralesHobby(
                    person_id=int(row['person_id']),
                    hobby=row['hobby']
                )
                hobbies_batch.append(hobby)

            session.add_all(hobbies_batch)

        # Seed studies
        print("Seeding studies...")
        with open(f"{csv_path}/studies_data.csv", 'r') as file:
            reader = csv.DictReader(file)
            studies_batch = []
            for row in reader:
                study = RandymoralesStudy(
                    person_id=int(row['person_id']),
                    degree=row['degree'],
                    institution=row['institution']
                )
                studies_batch.append(study)

            session.add_all(studies_batch)

        # Commit all changes
        session.commit()
        print("Successfully seeded all people data!")

        # Print summary statistics
        print(f"Total people: {session.query(RandymoralesPerson).count()}")
        print(f"Physical records: {session.query(RandymoralesPhysicalData).count()}")
        print(f"Family relations: {session.query(RandymoralesFamilyRelation).count()}")
        print(f"Favorite foods: {session.query(RandymoralesFavoriteFood).count()}")
        print(f"Hobbies: {session.query(RandymoralesHobby).count()}")
        print(f"Studies: {session.query(RandymoralesStudy).count()}")

    except Exception as e:
        session.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed_people_data()
