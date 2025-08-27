from sqlalchemy import select, or_
from deepdiff import DeepDiff
from database import get_session
from models import MonsterDanrodjim
from validators import ListMonsterResponseSchema, ListMonsterResponseSchema

import re

def update_database_monsters_list(monsters_list_api):
    session = get_session()
    monsters_list_db = session.execute(select(MonsterDanrodjim.index, MonsterDanrodjim.name, MonsterDanrodjim.url)).all()

    if len(monsters_list_db) == 0:
        monsters_to_add = []
        for monster in monsters_list_api:
            new_monster = MonsterDanrodjim(index=monster["index"], name=monster["name"], url=monster["url"])
            monsters_to_add.append(new_monster)
        session.add_all(monsters_to_add)
    else:
        schema = ListMonsterResponseSchema(many=True)
        monsters_list_db = schema.dump(monsters_list_db)
        diff = DeepDiff(monsters_list_db, monsters_list_api, ignore_order=True)
        if diff:
            for change_type, changes in diff.items():
                for key, value in changes.items():
                    if change_type == 'values_changed':
                        monster_to_update = session.query(MonsterDanrodjim).filter(
                            or_(
                                MonsterDanrodjim.index == value['old_value'],
                                MonsterDanrodjim.name == value['old_value'],
                                MonsterDanrodjim.url == value['old_value']
                            )
                        ).first()

                        matches = re.findall(r"\[(.*?)\]", key)

                        field_to_update = matches[1].strip("'")

                        if monster_to_update:
                            setattr(monster_to_update, field_to_update, value['new_value'])
                    elif change_type == 'iterable_item_added':
                        schema = ListMonsterResponseSchema()
                        new_monster = schema.load(value, session=session)
                        session.add(new_monster)
                    elif change_type == 'iterable_item_removed':
                        monster_to_delete = session.query(MonsterDanrodjim).filter_by(index=value["index"]).first()
                        if monster_to_delete:
                            session.delete(monster_to_delete)

    session.commit()
    session.close()
    return

def update_database_monsters_get(monster):
    session = get_session()
    monster_get = session.query(MonsterDanrodjim).filter_by(index=monster["index"]).first()
    if not monster_get:
        new_monster = {"index": monster["index"], "name": monster["name"], "url": monster["url"], "data": monster}
        schema = ListMonsterResponseSchema()
        new_monster = schema.load(new_monster, session=session)
        session.add(new_monster)
    else:
        monster_get.data = monster
    session.commit()
    session.close()

def get_monsters_list():
    session = get_session()
    monsters_list = session.execute(select(MonsterDanrodjim.index, MonsterDanrodjim.name, MonsterDanrodjim.url)).all()
    session.close()
    return monsters_list

def get_monster(monster):
    session = get_session()
    monster_get = session.query(MonsterDanrodjim).filter_by(index=monster).first()
    session.close()
    if not monster_get:
        return
    return monster_get