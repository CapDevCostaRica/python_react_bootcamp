import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))

from models import AndresnbozaMonster
from database import get_session

monsters = [
    "Beholder",
    "Mind Flayer",
    "Dragon",
    "Gelatinous Cube",
    "Mimic"
]

def seed_dnd_monsters():
    session = get_session()
    for name in monsters:
        session.add(AndresnbozaMonster(name=name))
    session.commit()
    session.close()
    print("Seeded Dnd Monsters")

if __name__ == "__main__":
    seed_dnd_monsters()
