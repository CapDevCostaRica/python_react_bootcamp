# Placeholder for Monster model
class Monster:
    def __init__(self, id, name, description="", stats=None):
        self.id = id
        self.name = name
        self.description = description
        self.stats = stats or {}
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "stats": self.stats
        }
