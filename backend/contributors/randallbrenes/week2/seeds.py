import pathlib
import pandas as pd
from app.database import get_session

base_path = pathlib.Path(__file__).resolve().parent / "data"
db = get_session()

def load_people():
    people_file = base_path / "people_data.csv"
    physical_file = base_path / "physical_data.csv"
    
    try:
        if people_file.exists() and physical_file.exists():
            df_people = pd.read_csv(people_file)
            df_physical = pd.read_csv(physical_file)

            df_merged = df_people.merge(
                df_physical,
                left_on="id",
                right_on="person_id",
                how="left"
            )
            df_merged.drop(columns=["person_id"], inplace=True)

            df_merged.to_sql("people", db.bind, if_exists="append", index=False)
            return True
        else:
            print("People or Physical data file does not exist.")
            return False
    except Exception as e:
        print(f"Error in load people: {e}")

    return False

def load_data():
    table_files = [
        "family",
        "favorite",
        "hobbies",
        "studies"
    ]
    print("...Starting data load...")
    if load_people():
        print("People loaded successfully.")

        for table in table_files:
            file_path = base_path / f"{table}_data.csv"

            if not file_path.exists():
                print(f"File for {table} does not exist, skipping.")
                continue

            try:
                df = pd.read_csv(file_path)
                df.to_sql(table, db.bind, if_exists='append', index=False)
                print(f"{table} loaded successfully.")
            except Exception as e:
                print(f"Error loading {table}: {e}")

    db.close()

if __name__ == "__main__":
    load_data()
