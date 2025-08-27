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
            
            api_data = self.api_client.get_monster(index)
            if not api_data:
                raise NotFoundError(f"Monster not found in external API: {index}")
            
            # Step 3: Transform API data to domain entity
            monster = Monster(
                index=index,
                name=api_data.get("name", "Unknown"),
                url=api_data.get("url", ""),
                data=api_data  # Store the complete API response
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


    def get_monster_list(self) -> CacheResult:
                    return CacheResult(
                data="[]",
                is_cached=False,
                source="api"
            )