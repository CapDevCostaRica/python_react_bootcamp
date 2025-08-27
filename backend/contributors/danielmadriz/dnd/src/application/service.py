"""
Implements the core caching strategy and monster management business logic.
"""
import logging
from ..domain.interfaces import IMonsterService, IMonsterRepository, IMonsterApiClient
from ..domain.entities import Monster, MonsterList, CacheResult
from ..helpers.exceptions import NotFoundError, ServiceError, ValidationError


class MonsterService(IMonsterService):
    
    def __init__(self, repository: IMonsterRepository, api_client: IMonsterApiClient):
        self.repository = repository
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
    
    def get_monster(self, index: str) -> CacheResult:
        try:
            # Validate input
            if not index or not isinstance(index, str):
                raise ValidationError("Monster index must be a non-empty string")
            
            self.logger.info(f"Getting monster: {index}")
            
            # Step 1: Check cache first (fast path)
            if self.repository.exists_monster(index):
                cached_monster = self.repository.get_monster(index)
                if cached_monster:
                    self.logger.info(f"Cache hit for monster: {index}")
                    return CacheResult(
                        data=cached_monster,
                        is_cached=True,
                        source="cache"
                    )
            
            # Step 2: Cache miss - fetch from external API
            self.logger.info(f"Cache miss for monster: {index}, fetching from API")
            
            if not self.api_client.is_available():
                raise ServiceError("External API is not available")
            
            api_data = self.api_client.get_monster(index)
            if not api_data:
                raise NotFoundError(f"Monster not found in external API: {index}")
            
            # Step 3: Transform API data to domain entity
            monster = Monster(
                index=index,
                name=api_data.get("name", "Unknown"),
                url=api_data.get("url", ""),
                data=api_data
            )
            
            # Step 4: Cache the result for future requests
            if self.repository.save_monster(monster):
                self.logger.info(f"Cached monster: {index}")
            else:
                self.logger.warning(f"Failed to cache monster: {index}")
            
            # Step 5: Return result with metadata
            return CacheResult(
                data=monster,
                is_cached=False,
                source="api"
            )
            
        except (ValidationError, ServiceError):
            raise
        except Exception as e:
            # Log unexpected errors and wrap in business exception
            self.logger.error(f"Unexpected error getting monster {index}: {str(e)}")
            raise ServiceError(f"Failed to get monster: {str(e)}")

        """Get complete monster list with caching strategy.
        
        Cache-Aside Pattern:
        1. Check local cache first
        2. If miss, fetch from external API
        3. Cache the result
        4. Return with metadata
        
        Returns:
            CacheResult with monster list and caching metadata
            
        Raises:
            ServiceError: If external API fails and no cache available
        """
        try:
            self.logger.info("Getting monster list")
            
            # Step 1: Check cache first (fast path)
            if self.repository.exists_monster_list():
                cached_list = self.repository.get_monster_list()
                if cached_list:
                    self.logger.info("Cache hit for monster list")
                    return CacheResult(
                        data=cached_list,
                        is_cached=True,
                        source="cache"
                    )
            
            # Step 2: Cache miss - fetch from external API
            self.logger.info("Cache miss for monster list, fetching from API")
            
            if not self.api_client.is_available():
                raise ServiceError("External API is not available")
            
            api_data = self.api_client.get_monster_list()
            if not api_data:
                raise ServiceError("Failed to fetch monster list from external API")
            
            # Step 3: Transform API data to domain entities
            monsters = []
            for monster_data in api_data.get("results", []):
                monster = Monster(
                    index=monster_data.get("index", ""),
                    name=monster_data.get("name", "Unknown"),
                    url=monster_data.get("url", ""),
                    data=monster_data
                )
                monsters.append(monster)
            
            monster_list = MonsterList(
                monsters=monsters,
                count=len(monsters)
            )
            
            # Step 4: Cache the result for future requests
            if self.repository.save_monster_list(monster_list):
                self.logger.info("Cached monster list")
            else:
                self.logger.warning("Failed to cache monster list")
            
            # Step 5: Return result with metadata
            return CacheResult(
                data=monster_list,
                is_cached=False,
                source="api"
            )
            
        except ServiceError:
            # Re-raise business exceptions
            raise
        except Exception as e:
            # Log unexpected errors and wrap in business exception
            self.logger.error(f"Unexpected error getting monster list: {str(e)}")
            raise ServiceError(f"Failed to get monster list: {str(e)}")

        """Refresh all cached data from external API.
        
        This method forces a cache refresh by:
        1. Fetching fresh data from external API
        2. Updating all cached data
        3. Ensuring cache consistency
        
        Returns:
            True if refresh successful, False otherwise
            
        Raises:
            ServiceError: If external API is not available
        """
        try:
            self.logger.info("Refreshing cache from external API")
            
            if not self.api_client.is_available():
                raise ServiceError("External API is not available")
            
            # Refresh monster list first
            monster_list_result = self.get_monster_list()
            if not monster_list_result.is_cached:
                self.logger.info("Monster list cache refreshed")
            
            # Refresh individual monsters (sample a few for efficiency)
            monster_list = monster_list_result.data
            if isinstance(monster_list, MonsterList) and monster_list.monsters:
                # Refresh first 5 monsters as a sample
                sample_monsters = monster_list.monsters[:5]
                for monster in sample_monsters:
                    try:
                        self.get_monster(monster.index)
                    except Exception as e:
                        self.logger.warning(f"Failed to refresh monster {monster.index}: {str(e)}")
            
            self.logger.info("Cache refresh completed successfully")
            return True
            
        except ServiceError:
            # Re-raise business exceptions
            raise
        except Exception as e:
            # Log unexpected errors and wrap in business exception
            self.logger.error(f"Unexpected error refreshing cache: {str(e)}")
            raise ServiceError(f"Failed to refresh cache: {str(e)}") 