import os
import sys
import logging
import pandas as pd
import heapq, csv
from pathlib import Path

from app.models import Base, Person, PhysicalAttribute, FamilyRelation, FavoriteFood, Hobby, Education

from database import get_session

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_if_seeded():
    """Check if database has already been seeded"""
    session = get_session()
    try:
        count = session.query(Person).count()
        return count > 0
    except Exception as e:
        logger.error(f"Error checking if database is seeded: {str(e)}")
        return False
    finally:
        session.close()

def read_complete_file_os_people():
    """Read file people_data.csv completely using os"""
    logger.info("Reading people_data.csv using os (entire file)")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, './files/people_data.csv')
    
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        
        lines = content.strip().split('\n')
        header = lines[0].split(',')
        
        data = []
        for i in range(1, len(lines)):
            row_values = lines[i].split(',')
            row_dict = {header[j]: row_values[j] for j in range(len(header))}
            data.append(row_dict)
        
        return data
    
    except Exception as e:
        logger.error(f"Error reading file with os: {str(e)}")
        return []
    
def read_physical_data_pandas_chunk():
    """Read physical_data.csv in chunks of 10 rows using pandas and bulk insert into PhysicalAttribute"""
    logger.info("Reading physical_data.csv in chunks of 10 rows using pandas")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, './files/physical_data.csv')
    
    session = get_session()
    try:
        chunk_size = 10
        total_inserted = 0
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            records = chunk.to_dict(orient='records')
            session.bulk_insert_mappings(PhysicalAttribute, records)
            session.commit()
            total_inserted += len(records)
            logger.info(f"Inserted chunk of {len(records)} records into PhysicalAttribute")
        logger.info(f"🚀 Total PhysicalAttribute records inserted: {total_inserted}")
    except Exception as e:
        logger.error(f"Error reading file with pandas or bulk inserting: {str(e)}")
        session.rollback()
    finally:
        session.close()

def read_family_data_heapq():
    """Read family_data.csv using heapq on CSV stream, ordered by person_id, renaming columns"""
    logger.info("Reading family_data.csv using heapq (streamed CSV)")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, './files/family_data.csv')
    heap = []
    counter = 0

    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                heapq.heappush(heap, (int(row['person_id']), counter, row))
                counter += 1
        sorted_rows = [heapq.heappop(heap)[2] for _ in range(len(heap))]
        # Renombrar las claves para coincidir con el modelo FamilyRelation
        renamed_rows = []
        for row in sorted_rows:
            renamed_rows.append({
                'person_id': int(row['person_id']),
                'relation_type': row['relation'],
                'relative_name': row['name']
            })
        logger.info(f"Total family relations loaded: {len(renamed_rows)}")
        return renamed_rows
    except Exception as e:
        logger.error(f"Error reading family_data.csv with heapq: {str(e)}")
        return []
    
def read_favorite_foods_pathlib_bulk():
    """Read favorite_data.csv using pathlib and bulk insert into FavoriteFood"""
    logger.info("Reading favorite_data.csv using pathlib (entire file)")
    base_dir = Path(__file__).parent
    file_path = base_dir / 'files' / 'favorite_data.csv'

    try:
        with file_path.open('r') as file:
            lines = file.read().strip().split('\n')
            header = lines[0].split(',')
            data = []
            for line in lines[1:]:
                values = line.split(',')
                row = {header[0]: int(values[0]), header[1]: values[1]}
                data.append(row)
        session = get_session()
        session.bulk_insert_mappings(FavoriteFood, data)
        session.commit()
        logger.info(f"🚀 Bulk insert completed: {len(data)} favorite foods")
    except Exception as e:
        logger.error(f"Error reading favorite_data.csv with pathlib or bulk insert: {str(e)}")
        if 'session' in locals():
            session.rollback()
    finally:
        if 'session' in locals():
            session.close()

def read_hobbies_pathlib_bulk():
    """Read hobbies_data.csv using pathlib and bulk insert into Hobby"""
    logger.info("Reading hobbies_data.csv using pathlib (entire file)")
    base_dir = Path(__file__).parent
    file_path = base_dir / 'files' / 'hobbies_data.csv'

    try:
        with file_path.open('r') as file:
            lines = file.read().strip().split('\n')
            header = lines[0].split(',')
            data = []
            for line in lines[1:]:
                values = line.split(',')
                row = {header[0]: int(values[0]), header[1]: values[1]}
                data.append(row)
        session = get_session()
        session.bulk_insert_mappings(Hobby, data)
        session.commit()
        logger.info(f"🚀 Bulk insert completed: {len(data)} hobbies")
    except Exception as e:
        logger.error(f"Error reading hobbies_data.csv with pathlib or bulk insert: {str(e)}")
        if 'session' in locals():
            session.rollback()
    finally:
        if 'session' in locals():
            session.close()

def read_studies_pathlib_bulk():
    """Read studies_data.csv using pathlib and bulk insert into Education"""
    logger.info("Reading studies_data.csv using pathlib (entire file)")
    base_dir = Path(__file__).parent
    file_path = base_dir / 'files' / 'studies_data.csv'

    try:
        with file_path.open('r') as file:
            lines = file.read().strip().split('\n')
            header = lines[0].split(',')
            data = []
            for line in lines[1:]:
                values = line.split(',')
                row = {header[j]: values[j] if j != 0 else int(values[j]) for j in range(len(header))}
                data.append(row)
        session = get_session()
        session.bulk_insert_mappings(Education, data)
        session.commit()
        logger.info(f"🚀 Bulk insert completed: {len(data)} studies")
    except Exception as e:
        logger.error(f"Error reading studies_data.csv with pathlib or bulk insert: {str(e)}")
        if 'session' in locals():
            session.rollback()
    finally:
        if 'session' in locals():
            session.close()

def orchestrator():
    people_dic = read_complete_file_os_people()
    
    session = get_session()
    try:
        session.bulk_insert_mappings(Person, people_dic)
        session.commit()
        logger.info(f"🚀 Bulk insert completed: {len(people_dic)} people")
    except Exception as e:
        logger.error(f"Error en bulk insert: {str(e)}")
        session.rollback()
    finally:
        session.close()

    read_physical_data_pandas_chunk()
    read_favorite_foods_pathlib_bulk()
    read_hobbies_pathlib_bulk()
    read_studies_pathlib_bulk()

    family_data = read_family_data_heapq()
    session = get_session()
    try:
        session.bulk_insert_mappings(FamilyRelation, family_data)
        session.commit()
        logger.info(f"🚀 Bulk insert completed: {len(family_data)} family relations")
    except Exception as e:
        logger.error(f"Error en bulk insert family relations: {str(e)}")
        session.rollback()
    finally:
        session.close()


def seed_database():
    """Seed the database with initial data"""
    session = get_session()
    try:
        if check_if_seeded():
            logger.info("🚀 Database is already seeded")
            return

        logger.info("Seeding database...")
        orchestrator()
        session.commit()
        logger.info("Database seeded successfully")
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()