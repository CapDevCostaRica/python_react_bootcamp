import os
import sys
from flask import Flask
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from app.config.seed_config import get_seed_config
from database import get_session
from pathlib import Path

app = Flask(__name__)
base_path = Path(__file__).resolve().parent

def get_csv_path(filename):
    #print (f"Base path: {base_path}")
    csv_path = base_path / ".." / ".." / ".." / ".." / "exercises" / "session_2" / "files" / filename
    resolved_path = csv_path.resolve()
    print(f"Path: {resolved_path}")
    return resolved_path


people_csv_path = get_csv_path("people_data.csv")
physical_csv_path = get_csv_path("physical_data.csv")
foods_csv_path = get_csv_path("favorite_data.csv")
hobbies_csv_path = get_csv_path("hobbies_data.csv")
studies_csv_path = get_csv_path("studies_data.csv")
family_csv_path = get_csv_path("family_data.csv")

csv_paths = {
    "people": people_csv_path,
    "physical": physical_csv_path,
    "foods": foods_csv_path,
    "hobbies": hobbies_csv_path,
    "studies": studies_csv_path,
    "family": family_csv_path
}

SEED_CONFIG = get_seed_config(csv_paths)

def seed_if_needed(session, name, config):
    if config["check"](session):
        print(f"{name} already seeded.")
    else:
        print(f"Seeding {name}...")
        config["seed"](session, *config["args"])
        print(f"{name} seeded.")
        
def is_data_seeded(session):
    for name, config in SEED_CONFIG.items():
        seed_if_needed(session, name, config)

@app.route('/')
def health():
    return {'status': 'here_ok'}

if __name__ == '__main__':
    session = get_session()
    is_data_seeded(session)
    app.run(host='0.0.0.0', port=4000)
