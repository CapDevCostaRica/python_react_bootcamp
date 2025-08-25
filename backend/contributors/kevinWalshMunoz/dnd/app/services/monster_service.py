# Monster service functions
from app.models import Monster

def get_all_monsters():
    """Return a list of all monster names"""
    from app.services import get_all_monsters as service_get_all_monsters
    return service_get_all_monsters()

def get_monster_by_index(index):
    """Get a monster's details by its index"""
    from app.services import get_monster_by_index as service_get_monster_by_index
    return service_get_monster_by_index(index)
