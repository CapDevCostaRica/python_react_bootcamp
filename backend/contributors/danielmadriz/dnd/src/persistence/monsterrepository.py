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
                    data= monster.data
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
            raise CacheError(f"Failed to retrieve monster: {str(e)}")
        finally:
            session.close()
    
    def get_monster_list(self) -> Optional[MonsterList]:
        session = self._get_session()
        try:
            # Query monster list from database
            result = session.query(AllMonstersdanielmadriz).order_by(
                AllMonstersdanielmadriz.index.desc()
            ).first()
            
            if not result:
                self.logger.info("Monster list not found in cache")
                return None
            
            # Extract monster list data from JSON
            data = result.data
            monsters_data = data.get('monsters', [])
            count = data.get('count', 0)
            
            monsters = []
            for monster_data in monsters_data:
                monster = Monster(
                    index=monster_data.get('index', ''),
                    name=monster_data.get('name', 'Unknown'),
                    url=monster_data.get('url', ''),
                    data=monster_data
                )
                monsters.append(monster)
            
            monster_list = MonsterList(
                monsters=monsters,
                count=count
            )
            
            self.logger.info("Monster list retrieved from cache")
            return monster_list
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve monster list: {str(e)}")
            raise CacheError(f"Failed to retrieve monster list: {str(e)}")
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
            raise CacheError(f"Failed to check monster existence: {str(e)}")
        finally:
            session.close()