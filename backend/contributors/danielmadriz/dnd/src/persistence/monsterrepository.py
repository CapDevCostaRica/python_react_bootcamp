"""
Infrastructure Layer - Data persistence implementation.
Implements the repository interface for monster data storage.
"""
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))

from typing import Optional, Dict, Any
from ..domain.interfaces import IMonsterRepository
from ..domain.entities import Monster, MonsterList
from ..helpers.exceptions import CacheError
from framework.database import get_session
from framework.models import Monstersdanielmadriz, AllMonstersdanielmadriz
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
            # Check if monster already exists
            existing_monster = session.query(Monstersdanielmadriz).filter(
                Monstersdanielmadriz.id == monster.index
            ).first()
            
            if existing_monster:
                # Update existing monster
                existing_monster.json_data = {
                    'index': monster.index,
                    'name': monster.name,
                    'url': monster.url,
                    'data': monster.data
                }
                self.logger.info(f"Monster updated: {monster.index}")
            else:
                # Create new monster
                new_monster = Monstersdanielmadriz(
                    id=monster.index,
                    json_data={
                        'index': monster.index,
                        'name': monster.name,
                        'url': monster.url,
                        'data': monster.data
                    }
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
                Monstersdanielmadriz.id == index
            ).first()
            
            if not result:
                self.logger.info(f"Monster not found in cache: {index}")
                return None
            
            json_data = result.json_data
            monster_data = json_data.get('data', {})
            
            monster = Monster(
                index=json_data.get('index', index),
                name=json_data.get('name', 'Unknown'),
                url=json_data.get('url', ''),
                properties=monster_data
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
                AllMonstersdanielmadriz.id.desc()
            ).first()
            
            if not result:
                self.logger.info("Monster list not found in cache")
                return None
            
            # Extract monster list data from JSON
            json_data = result.json_data
            monsters_data = json_data.get('monsters', [])
            count = json_data.get('count', 0)
            
            monsters = []
            for monster_data in monsters_data:
                monster = Monster(
                    index=monster_data.get('index', ''),
                    name=monster_data.get('name', 'Unknown'),
                    url=monster_data.get('url', ''),
                    properties=monster_data
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
                Monstersdanielmadriz.id == index
            ).first()
            
            exists = result is not None
            self.logger.debug(f"Monster exists {index}: {exists}")
            return exists
            
        except Exception as e:
            self.logger.error(f"Failed to check monster existence {index}: {str(e)}")
            raise CacheError(f"Failed to check monster existence: {str(e)}")
        finally:
            session.close()