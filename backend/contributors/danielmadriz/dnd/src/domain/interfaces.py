"""
Domain Layer - Abstract interfaces and contracts.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from src.domain.entities.monster import Monster
from src.domain.entities.monster_list import MonsterList
from src.domain.entities.cache_result import CacheResult


class IMonsterRepository(ABC):
    
    @abstractmethod
    def save_monster(self, monster: Monster) -> bool:
        """Save a monster to persistent storage."""
        pass
    
    @abstractmethod
    def get_monster(self, index: str) -> Optional[Monster]:
        """Retrieve a monster by index from persistent storage."""
        pass
    
    @abstractmethod
    def get_monster_list(self) -> Optional[MonsterList]:
        """Retrieve the complete list of monsters from persistent storage."""
        pass
    
    @abstractmethod
    def save_monster_list(self, monster_list: MonsterList) -> bool:
        """Save the complete list of monsters to persistent storage."""
        pass
    
    @abstractmethod
    def exists_monster(self, index: str) -> bool:
        """Check if a monster exists in persistent storage."""
        pass


class IMonsterApiClient(ABC):
    """
    External API client interface for D&D 5e API.
    Provides flexibility for testing and switching API data source
    """
    
    @abstractmethod
    def get_monster(self, index: str) -> Optional[Dict[str, Any]]:
        """Fetch monster data from external API."""
        pass
    
    @abstractmethod
    def get_monster_list(self) -> Optional[Dict[str, Any]]:
        """Fetch complete monster list from external API."""
        pass


class IMonsterService(ABC):
    """
    Business logic service interface for monster operations.
    Focused on business logic orchestration only
    No data access or external API concerns
    """
    
    @abstractmethod
    def get_monster(self, index: str) -> CacheResult:
        """Get monster with caching strategy (Cache-Aside pattern)."""
        pass
    
    @abstractmethod
    def get_monster_list(self) -> CacheResult:
        """Get monster list with caching strategy (Cache-Aside pattern)."""
        pass


 