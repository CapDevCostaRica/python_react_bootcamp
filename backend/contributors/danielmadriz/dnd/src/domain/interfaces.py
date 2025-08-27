"""
Domain Layer - Abstract interfaces and contracts.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from .entities import Monster, MonsterList, CacheResult


class IMonsterRepository(ABC):
    """
    Repository interface for monster data persistence.
    """
    
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
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if external API is available. This is for sanity check"""
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


class IValidator(ABC):
    """
    Validation interface for input/output data.
    Focused on data validation only
    """
    
    @abstractmethod
    def validate_monster_request(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate monster request payload.
        Returns:
            tuple: (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def validate_monster_list_request(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate monster list request payload.
        Returns:
            tuple: (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def validate_monster_data(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate monster data structure from external API.
        Returns:
            tuple: (is_valid, error_message)
        """
        pass 