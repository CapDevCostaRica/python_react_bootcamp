"""
Infrastructure Layer - Data persistence implementation.
Implements the repository interface for monster data storage.
"""
import logging
import sys
import os
from datetime import datetime
from typing import Optional
from ..domain.interfaces import IMonsterRepository
from ..domain.entities import Monster, MonsterList
from ..helpers.exceptions import CacheError

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
            result = session.query(AllMonstersdanielmadriz)
            
            data = result.json_data
            monsters_data = data.get('monsters', [])
            count = data.get('count', 0)
            
            if monsters_data and count > 0:
                monsters = []
                for monster_data in monsters_data:
                    monster = Monster(
                        index=monster_data.get('index', ''),
                        name=monster_data.get('name', 'Unknown'),
                        url=monster_data.get('url', ''),
                        data=monster_data
                    )
                    monsters.append(monster)
                
                self.logger.info(f"Monster list retrieved from cache: {count} monsters (key data only)")
                return monsters
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
            # Check if monster list already exists
            existing_list = session.query(AllMonstersdanielmadriz).first()
            
            if existing_list:
                self.logger.info("Monster list already exists in cache, skipping save")
                return True
            else:
                # Create new monster list entry
                new_monster_list = AllMonstersdanielmadriz(
                    json_data={
                        'monsters': [
                            {
                                'index': monster.index,
                                'name': monster.name,
                                'url': monster.url
                            }
                            for monster in monster_list.monsters
                        ],
                        'count': monster_list.count,
                        'cached_at': datetime.utcnow().isoformat(),
                        'source': 'dnd5e_api'
                    }
                )
                session.add(new_monster_list)
                self.logger.info(f"Monster list cached with {monster_list.count} monsters")
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
