from marshmallow import ValidationError
from schemas.response import ResponseGetSchema, ResponseListSchema
from models import RandallBrenesDnD
from DnDApi import DnDApi
class Monsters:
    def __init__(self, db):
        self._db = db
        self._api = DnDApi()
        self._model = RandallBrenesDnD
        self._schema_all = ResponseListSchema()
        self._schema_single = ResponseGetSchema()

    def get_all(self):
        monsters_list = self._api.list()
        from_database = self._db.query(self._model).all()
        
        db_monsters = {monster.index: monster for monster in from_database}
        all_monsters = []
        has_new_monster = False
        for monster_data in monsters_list["results"]:
            index = monster_data.get("index")
            if index in db_monsters:
                # Monster exists in DB, use DB object
                all_monsters.append(monster_data)
                del db_monsters[index]
            else:
                # Monster is new, create DB object and add
                new_monster = self._model(**monster_data)
                self._db.add(new_monster)
                all_monsters.append(monster_data)
                has_new_monster = True
        
        if has_new_monster:
            self._db.commit()

        if db_monsters:
            # monsters on db that isn't on API
            for monster in db_monsters:
                all_monsters.append(db_monsters[monster])
        to_return = []
        try:
            to_return = self._schema_all.dump({"count": len(all_monsters), "results": all_monsters}) #  self._schema_all.dump({"count": len(all_monsters), "results": all_monsters})        
        except ValidationError as err:
            to_return = {"error": err.messages}
        except Exception as x:
            to_return = {"error": x}
        finally: 
            return to_return

    def get_single(self, monster_index: str):
        monster_from_database = self._db.query(self._model).filter(self._model.index == monster_index).one_or_none()

        if monster_from_database is not None and monster_from_database.type:
            return self._schema_single.dump(monster_from_database)
        else:
            monster_from_api = self._api.get(monster_index)
            if monster_from_api is not None:
                try:
                    new_monster = self._model(**monster_from_api)
                    if monster_from_database is None:
                        self._db.add(new_monster)
                    else:
                        self._db.merge(new_monster)
                    self._db.commit()
                except Exception as ex:
                    print("Error trying to save on db ", str(ex))
                return self._schema_single.dump(new_monster)

            return None