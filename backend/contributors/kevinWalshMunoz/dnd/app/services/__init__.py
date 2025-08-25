from app.models import Monster

# Mock data - in a real app this would come from a database
mock_monsters = [
    Monster("monster1", "Goblin", "Small, green and mean", {"HP": 7, "AC": 15}),
    Monster("monster2", "Orc", "Large, green and mean", {"HP": 15, "AC": 13})
]

def get_all_monsters():
    """Return a list of all monster names"""
    return [monster.id for monster in mock_monsters]

def get_monster_by_index(index):
    """Get a monster's details by its index"""
    # In a real app, you would search in the database
    for monster in mock_monsters:
        if monster.id == index:
            return monster.to_dict()
    return f"Datos del monstruo {index}" # Placeholder for when monster not found
