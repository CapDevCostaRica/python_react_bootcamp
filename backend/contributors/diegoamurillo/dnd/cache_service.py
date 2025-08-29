import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from models import DMuriMonster
from models import DMuriMonstersList
from database import get_session

class CacheService:
    def __init__(self, upstream_service):
        self.upstream_service = upstream_service
    
    def get_monsters_list(self):
        session = get_session()
        monsters_list = session.query(DMuriMonstersList).all()
        
        if monsters_list:
            session.close()
            return monsters_list.data
        
        upstream_monsters = self.upstream_service.get_monsters_list()

        if upstream_monsters: 
            monsters_list = DMuriMonstersList(
                id = 1,
                data = upstream_monsters
            )
            session.add(monsters_list)
            session.close()
        
            return upstream_monsters
        
        session.close()
        return []
    
    def get_monster_by_index(self, monster_index):
        session = get_session()
        monster = session.query(DMuriMonster).filter_by(index=monster_index).first()
        
        if monster:
            session.close()
            return monster.data
        
        upstream_monster = self.upstream_service.get_monster_by_index(monster_index)
        
        if upstream_monster:
            monster = DMuriMonster(
                index=upstream_monster.get('index'),
                data = upstream_monster
            )
            session.add(monster)
            session.close()
            
            return upstream_monster
        session.close()
        return None