import os
import sys
from pathlib import Path
from typing import List, Any, Optional, Callable
import pandas as pd
# Add app path first for local models
app_path = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_path)

# Import local models first
from models import Person, PhysicalProfile, FavoriteFood, Hobby, FamilyRelation, Study
from logger_config.loggerconfig import setup_application_logging, get_logger
from mappers.dataframe_mapper import DataFrameMapper

# Add framework path for database access
framework_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'framework')
if framework_path not in sys.path:
    sys.path.insert(0, framework_path)

from database import get_session

setup_application_logging()
logger = get_logger(__name__)

BATCH_SIZE = 1000
CSV_FILES_DIR = Path(__file__).parent / "files"
CSV_ENCODING = 'utf-8'

mapper = DataFrameMapper()

def process_people_data(session) -> int:
    logger.info("Processing people_data.csv")
    csv_path = CSV_FILES_DIR / "people_data.csv"
    
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    df = _read_csv_file_to_dataframe(csv_path)
    if df.empty:
        return 0
    
    batch_data = []
    processed_count = 0
    
    people_objects = mapper.process_people_dataframe(df)
    
    for i, person in enumerate(people_objects):
        csv_id = int(df.iloc[i]['id'])
        full_name = person.full_name
        
        existing_person = session.query(Person).filter(
            Person.id == csv_id
        ).first()
        
        if existing_person:
            continue  # Skip existing person
        
        person.id = csv_id
        batch_data.append(person)
        
        if len(batch_data) >= BATCH_SIZE:
            session.add_all(batch_data)
            session.flush() 
            processed_count += len(batch_data)
            batch_data = []
    
    if batch_data:
        session.add_all(batch_data)
        session.flush()
        processed_count += len(batch_data)
    
    session.commit()
    logger.info(f"Processed {processed_count} people")
    
    return processed_count

def process_physical_data(session):
    csv_path = CSV_FILES_DIR / "physical_data.csv"
    return _process_csv_data(
        session, csv_path, mapper.process_physical_dataframe, 
        "physical profiles", _check_physical_profile_exists
    )

def process_favorite_foods(session):
    csv_path = CSV_FILES_DIR / "favorite_data.csv"
    return _process_csv_data(
        session, csv_path, mapper.process_favorite_food_dataframe, 
        "favorite foods", _check_favorite_food_exists
    )

def process_hobbies(session):
    csv_path = CSV_FILES_DIR / "hobbies_data.csv"
    return _process_csv_data(
        session, csv_path, mapper.process_hobby_dataframe, 
        "hobbies", _check_hobby_exists
    )

def process_family_relations(session):
    csv_path = CSV_FILES_DIR / "family_data.csv"
    return _process_csv_data(
        session, csv_path, mapper.process_family_relation_dataframe, 
        "family relations", _check_family_relation_exists
    )

def process_studies(session):
    csv_path = CSV_FILES_DIR / "studies_data.csv"
    return _process_csv_data(
        session, csv_path, mapper.process_study_dataframe, 
        "studies", _check_study_exists
    )

def check_existing_data(session):
    existing_people = session.query(Person).count()
    if existing_people > 0:
        logger.warning(f"WARNING: {existing_people} people already exist in database. Skipping existing records")
        logger.info("="*50)
        return True  # Return True if data exists
    return False  # Return False if no data exists

def _read_csv_file_to_dataframe(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        logger.warning(f"CSV file not found: {csv_path}")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(csv_path, encoding=CSV_ENCODING)
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        logger.error(f"Error reading CSV file {csv_path}: {e}")
        return pd.DataFrame()

def _process_batch(session, batch: List[Any], batch_name: str) -> int:
    if not batch:
        return 0
    
    try:
        session.add_all(batch)
        session.commit()
        processed_count = len(batch)
        logger.debug(f"Processed batch of {processed_count} {batch_name}")
        return processed_count
    except Exception as e:
        session.rollback()
        logger.error(f"Error processing batch of {batch_name}: {e}")
        # Try to process items individually to identify problematic records
        individual_count = 0
        for item in batch:
            try:
                session.add(item)
                session.commit()
                individual_count += 1
            except Exception as individual_error:
                session.rollback()
                logger.warning(f"Skipping duplicate or invalid {batch_name}: {individual_error}")
        return individual_count

def _process_csv_data(
    session,
    csv_path: Path,
    process_dataframe_func: Callable[[pd.DataFrame], List[Any]],
    batch_name: str,
    check_existence_func: Optional[Callable] = None
) -> int:
    logger.info(f"Processing {csv_path.name}")
    
    df = _read_csv_file_to_dataframe(csv_path)
    if df.empty:
        return 0
    
    # Process the entire DataFrame at once
    objects = process_dataframe_func(df)
    if not objects:
        return 0
    
    if check_existence_func:
        filtered_objects = []
        for obj in objects:
            if not check_existence_func(session, obj):
                filtered_objects.append(obj)
        objects = filtered_objects
    
    processed_count = 0
    for i in range(0, len(objects), BATCH_SIZE):
        batch = objects[i:i + BATCH_SIZE]
        processed_count += _process_batch(session, batch, batch_name)
    
    logger.info(f"Processed {processed_count} {batch_name}")
    return processed_count

def _check_physical_profile_exists(session, profile: PhysicalProfile) -> bool:
    return session.query(PhysicalProfile).filter(
        PhysicalProfile.person_id == profile.person_id
    ).first() is not None

def _check_favorite_food_exists(session, favorite_food: FavoriteFood) -> bool:
    return session.query(FavoriteFood).filter(
        FavoriteFood.person_id == favorite_food.person_id,
        FavoriteFood.food == favorite_food.food
    ).first() is not None

def _check_hobby_exists(session, hobby: Hobby) -> bool:
    return session.query(Hobby).filter(
        Hobby.person_id == hobby.person_id,
        Hobby.hobby == hobby.hobby
    ).first() is not None

def _check_family_relation_exists(session, family_relation: FamilyRelation) -> bool:
    return session.query(FamilyRelation).filter(
        FamilyRelation.person_id == family_relation.person_id,
        FamilyRelation.relation == family_relation.relation,
        FamilyRelation.name == family_relation.name
    ).first() is not None

def _check_study_exists(session, study: Study) -> bool:
    return session.query(Study).filter(
        Study.person_id == study.person_id,
        Study.degree == study.degree,
        Study.institution == study.institution
    ).first() is not None


def seed_all_data():
    logger.info("Starting health database seeding process for exercise 2")
    
    # Get database session
    session = get_session()
    
    try:
        # Check if data already exists
        if check_existing_data(session):
            logger.info("Database already contains data. Seeding process completed successfully (no new data needed).")
            return
        
        total_processed = 0
        
        # 1. Process people data
        people_count = process_people_data(session)
        total_processed += people_count
        logger.info(f"People seeding completed: {people_count} records")
        
        # 2. Process physical profiles
        physical_count = process_physical_data(session)
        total_processed += physical_count
        logger.info(f"Physical profiles seeding completed: {physical_count} records")
        
        # 3. Process favorite foods
        foods_count = process_favorite_foods(session)
        total_processed += foods_count
        logger.info(f"Favorite foods seeding completed: {foods_count} records")
        
        # 4. Process hobbies
        hobbies_count = process_hobbies(session)
        total_processed += hobbies_count
        logger.info(f"Hobbies seeding completed: {hobbies_count} records")
        
        # 5. Process family relations
        family_count = process_family_relations(session)
        total_processed += family_count
        logger.info(f"Family relations seeding completed: {family_count} records")
        
        # 6. Process studies
        studies_count = process_studies(session)
        total_processed += studies_count
        logger.info(f"Studies seeding completed: {studies_count} records")
        
        logger.info(f"Database seeding completed successfully! Total records processed: {total_processed}")
        
    except Exception as e:
        logger.error(f"Error during database seeding: {str(e)}", exc_info=True)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_all_data()