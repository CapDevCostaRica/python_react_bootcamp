"""
Infrastructure Layer - Data persistence implementation.
Implements the repository interface for monster data storage.
"""
import logging
import sys
from datetime import datetime
from typing import Optional

from src.domain.interfaces import IMonsterRepository
from src.domain.entities.monster import Monster
from src.domain.entities.monster_list import MonsterList
from src.helpers.exceptions import CacheError

import sys
sys.path.append('/app/framework')
from database import get_session
from models import Monstersdanielmadriz, AllMonstersdanielmadriz
from sqlalchemy.orm import Session


class MonsterRepository(IMonsterRepository):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("PostgreSQL Monster Repository initialized")
    
    def _get_session(self) -> Session:
        return get_session()
    
    def save_monster(self, monster: Monster) -> bool:
        session = self._get_session()
        try:
            existing_monster = session.query(Monstersdanielmadriz).filter(
                Monstersdanielmadriz.index == monster.index
            ).first()
            
            if existing_monster:
                self.logger.info(f"Monster already exists in cache, skipping save: {monster.index}")
                return True
            else:
                new_monster = Monstersdanielmadriz(
                    index=monster.index,
                    name=monster.name,
                    url=monster.url,
                    data=monster.data
                )
                session.add(new_monster)
                self.logger.info(f"Monster created: {monster.index}")
                session.commit()
            
            return True
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to save monster {monster.index}: {str(e)}")
            raise CacheError(f"Failed to save monster: {str(e)}")
        finally:
            session.close()
    
    def get_monster(self, index: str) -> Optional[Monster]:
        session = self._get_session()
        try:
            result = session.query(Monstersdanielmadriz).filter(
                Monstersdanielmadriz.index == index
            ).first()
            
            if not result:
                self.logger.info(f"Monster not found in cache: {index}")
                return None

            monster = Monster(
                index=result.index,
                name=result.name,
                url=result.url,
                data=result.data
            )
            
            self.logger.info(f"Monster retrieved from cache: {index}")
            return monster
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve monster {index}: {str(e)}")
            raise CacheError(f"Failed to retrieve monster {index}: {str(e)}")
        finally:
            session.close()
    
    def get_monster_list(self) -> Optional[MonsterList]:
        session = self._get_session()
        try:
            result = session.query(AllMonstersdanielmadriz).first()
            
            if not result:
                self.logger.info("Monster list not found in cache")
                return None
            
            all_monsters = session.query(AllMonstersdanielmadriz).all()
            
            if all_monsters and len(all_monsters) > 0:
                monsters = []
                for monster_row in all_monsters:
                    monster_data = monster_row.json_data
                    monster = Monster(
                        index=monster_data.get('index', ''),
                        name=monster_data.get('name', 'Unknown'),
                        url=monster_data.get('url', ''),
                        data=monster_data
                    )
                    monsters.append(monster)
                
                monster_list = MonsterList(
                    monsters=monsters,
                    count=len(monsters)
                )
                
                self.logger.info(f"Monster list retrieved from cache: {len(monsters)} monsters (individual rows)")
                return monster_list
            else:
                self.logger.info("Monster list is empty")
                return None
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve monster list: {str(e)}")
            raise CacheError(f"Failed to retrieve monster list: {str(e)}")
        finally:
            session.close()
    
    def save_monster_list(self, monster_list: MonsterList) -> bool:
        session = self._get_session()
        try:
            existing_list = session.query(AllMonstersdanielmadriz).first()
            
            if existing_list:
                self.logger.info("Monster list already exists in cache, skipping save")
                return True
            else:
                for monster in monster_list.monsters:
                    new_monster_list = AllMonstersdanielmadriz(
                        id=monster.index,
                        json_data={
                            'index': monster.index,
                            'name': monster.name,
                            'url': monster.url,
                            'data': monster.data
                        }
                    )
                    session.add(new_monster_list)
                
                self.logger.info(f"Monster list cached with {monster_list.count} monsters (individual rows)")
                session.commit()
            
            return True
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to save monster list: {str(e)}")
            raise CacheError(f"Failed to save monster list: {str(e)}")
        finally:
            session.close()
    
    def exists_monster(self, index: str) -> bool:
        session = self._get_session()
        try:
            result = session.query(Monstersdanielmadriz).filter(
                Monstersdanielmadriz.index == index
            ).first()
            
            exists = result is not None
            self.logger.debug(f"Monster exists {index}: {exists}")
            return exists
            
        except Exception as e:
            self.logger.error(f"Failed to check monster existence {index}: {str(e)}")
            raise CacheError(f"Failed to check monster existence {index}: {str(e)}")
        finally:
            session.close()
