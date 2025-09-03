import os
import sys
from pathlib import Path
from typing import List, Any, Optional, Callable
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
from models import Person, PhysicalProfile, FavoriteFood, Hobby, FamilyRelation, Study
from logger_config.loggerconfig import setup_application_logging, get_logger
from mappers.dataframe_mapper import DataFrameMapper

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
    _process_csv_data(
        session, csv_path, mapper.process_physical_dataframe, 
        "physical profiles", _check_physical_profile_exists
    )

def process_favorite_foods(session):
    csv_path = CSV_FILES_DIR / "favorite_data.csv"
    _process_csv_data(
        session, csv_path, mapper.process_favorite_food_dataframe, 
        "favorite foods", _check_favorite_food_exists
    )

def process_hobbies(session):
    csv_path = CSV_FILES_DIR / "hobbies_data.csv"
    _process_csv_data(
        session, csv_path, mapper.process_hobby_dataframe, 
        "hobbies", _check_hobby_exists
    )

def process_family_relations(session):
    csv_path = CSV_FILES_DIR / "family_data.csv"
    _process_csv_data(
        session, csv_path, mapper.process_family_relation_dataframe, 
        "family relations", _check_family_relation_exists
    )

def process_studies(session):
    csv_path = CSV_FILES_DIR / "studies_data.csv"
    _process_csv_data(
        session, csv_path, mapper.process_study_dataframe, 
        "studies", _check_study_exists
    )

def check_existing_data(session):
    existing_people = session.query(Person).count()
    if existing_people > 0:
        logger.warning(f"WARNING: {existing_people} people already exist in database. Skipping existing records")
        logger.info("="*50)

def _read_csv_file_to_dataframe(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        logger.warning(f"CSV file not found: {csv_path}")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(csv_path, encoding=CSV_ENCODING)
        string_columns = df.select_dtypes(include=['object']).columns
        df[string_columns] = df[string_columns].astype(str).str.strip()
        return df
    except Exception as e:
        logger.error(f"Error reading CSV file {csv_path}: {e}")
        return pd.DataFrame()

def _process_batch(session, batch: List[Any], batch_name: str) -> int:
    if not batch:
        return 0
    
    session.add_all(batch)
    session.commit()
    processed_count = len(batch)
    logger.debug(f"Processed batch of {processed_count} {batch_name}")
    return processed_count

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
