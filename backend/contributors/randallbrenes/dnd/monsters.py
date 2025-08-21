from dnd_schema import DnDMinSchema, DnDSchema
from models import RandallBrenesDnD
from DnDApi import DnDApi

class Monsters:
    def __init__(self, db):
        self._db = db
        self._api = DnDApi()
        self._model = RandallBrenesDnD
        self._schema_single = DnDSchema()
        self._schema_all = DnDMinSchema(many=True)

    def get_all(self):
        from_database = self._db.query(self._model).all()
        if from_database:
            return self._schema_all.dump(from_database)
        else:
            monsters_list = self._api.list()
            if monsters_list != None:
                for monster in monsters_list:
                    self._db.add(self._model(**monster))
                self._db.commit()
                return monsters_list
            else:
                print("Failed to fetch all monsters from API")                
                return None

    def get_single(self, monster_index: str):
        from_database = self._db.query(self._model).filter(self._model.index == monster_index).one_or_none()
        if from_database is not None and from_database.type:
            return self._schema_single.dump(from_database)
        else:
            monster = self._api.get(monster_index)
            if monster is not None:
                new_object = self._model(**monster)
                if from_database is None:
                    self._db.add(new_object)
                else:
                    self._db.merge(new_object)
                self._db.commit()
                return monster
        
            print("Failed to fetch single monster data from API")
            return None