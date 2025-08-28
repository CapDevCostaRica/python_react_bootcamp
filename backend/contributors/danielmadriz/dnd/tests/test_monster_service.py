"""
Unit tests for MonsterService class
"""
import pytest
from unittest.mock import Mock
from src.application.service import MonsterService
from src.domain.entities.monster import Monster
from src.domain.entities.monster_list import MonsterList
from src.domain.entities.cache_result import CacheResult
from src.helpers.exceptions import ServiceError, ValidationError


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def mock_api_client():
    return Mock()


@pytest.fixture
def monster_service(mock_repository, mock_api_client):
    return MonsterService(
        repository=mock_repository,
        api_client=mock_api_client
    )


class TestMonsterService:
    
    def test_get_monster_list_cache_hit(self, monster_service, mock_repository, mock_api_client):
        # Arrange
        mock_monsters = [
            Monster(index="dragon", name="Dragon", url="/api/monsters/dragon", data={}),
            Monster(index="goblin", name="Goblin", url="/api/monsters/goblin", data={})
        ]
        mock_monster_list = MonsterList(monsters=mock_monsters, count=2)
        
        mock_repository.get_monster_list.return_value = mock_monster_list
        
        # Act
        result = monster_service.get_monster_list()
        
        # Assert
        assert isinstance(result, CacheResult)
        assert result.is_cached is True
        assert result.source == "cache"
        assert result.data == mock_monster_list
        assert result.data.count == 2
        assert len(result.data.monsters) == 2
        
        # Verify repository was called
        mock_repository.get_monster_list.assert_called_once()
        
        # Verify API client was NOT called (cache hit)
        mock_api_client.get_monster_list.assert_not_called()

    def test_get_monster_list_cache_miss_then_hit(self, monster_service, mock_repository, mock_api_client):
        # Arrange
        mock_repository.get_monster_list.return_value = None  # Cache is empty
        
        api_response = {
            "count": 2,
            "results": [
                {"index": "dragon", "name": "Dragon", "url": "/api/monsters/dragon", "data": {"type": "dragon"}},
                {"index": "goblin", "name": "Goblin", "url": "/api/monsters/goblin", "data": {"type": "goblin"}}
            ]
        }
        mock_api_client.get_monster_list.return_value = api_response
        
        mock_repository.save_monster_list.return_value = True
        
        # Act
        result1 = monster_service.get_monster_list()
        
        # Assert
        assert isinstance(result1, CacheResult)
        assert result1.is_cached is False
        assert result1.source == "api"
        assert result1.data.count == 2
        assert len(result1.data.monsters) == 2
        
        # Verify API was called and repository save was attempted
        mock_api_client.get_monster_list.assert_called_once()
        mock_repository.save_monster_list.assert_called_once()
        
        # Arrange - Second call: cache hit
        mock_monsters = [
            Monster(index="dragon", name="Dragon", url="/api/monsters/dragon", data={"type": "dragon"}),
            Monster(index="goblin", name="Goblin", url="/api/monsters/goblin", data={"type": "goblin"})
        ]
        mock_monster_list = MonsterList(monsters=mock_monsters, count=2)
        mock_repository.get_monster_list.return_value = mock_monster_list
        
        mock_api_client.get_monster_list.reset_mock()
        mock_repository.save_monster_list.reset_mock()
        
        # Act
        result2 = monster_service.get_monster_list()
        
        # Assert
        assert isinstance(result2, CacheResult)
        assert result2.is_cached is True
        assert result2.source == "cache"
        assert result2.data.count == 2
        assert len(result2.data.monsters) == 2
        
        # Verify API was NOT called again (cache hit)
        mock_api_client.get_monster_list.assert_not_called()
        
        # Verify no additional save attempts
        mock_repository.save_monster_list.assert_not_called()

    def test_get_monster_list_api_not_found_error(self, monster_service, mock_repository, mock_api_client):
        # Arrange 
        mock_repository.get_monster_list.return_value = None
        
        mock_api_client.get_monster_list.return_value = None
        
        # Act
        with pytest.raises(ServiceError) as exc_info:
            monster_service.get_monster_list()
        
        # Assert
        assert "Failed to fetch monster list from external API" in str(exc_info.value)
        
        # Verify repository get was called (to check cache first)
        mock_repository.get_monster_list.assert_called_once()

        # Verify API was called
        mock_api_client.get_monster_list.assert_called_once()
        
        # Verify repository save was NOT attempted (since API failed)
        mock_repository.save_monster_list.assert_not_called()
        
    def test_get_monster_empty_key_error(self, monster_service, mock_repository, mock_api_client):
        # Arrange
        empty_index = ""
        
        # Act
        with pytest.raises(ValidationError) as exc_info:
            monster_service.get_monster(empty_index)
        
        # Assert
        assert "Monster index must be a non-empty string" in str(exc_info.value)
        
        # Verify repository was NOT called (validation failed before reaching repository)
        mock_repository.exists_monster.assert_not_called()
        mock_repository.get_monster.assert_not_called()
        
        # Verify API was NOT called (validation failed before reaching API)
        mock_api_client.get_monster.assert_not_called()

    def test_get_monster_cache_hit(self, monster_service, mock_repository, mock_api_client):
        # Arrange
        mock_monster = Monster(index="dragon", name="Dragon", url="/api/monsters/dragon", data={"type": "dragon", "size": "huge"})
        mock_repository.exists_monster.return_value = True
        mock_repository.get_monster.return_value = mock_monster
        
        # Act
        result = monster_service.get_monster("dragon")
        
        # Assert
        assert isinstance(result, CacheResult)
        assert result.is_cached is True
        assert result.source == "cache"
        assert result.data == mock_monster
        assert result.data.index == "dragon"
        assert result.data.name == "Dragon"
        assert result.data.data["type"] == "dragon"
        
        # Verify repository methods were called
        mock_repository.exists_monster.assert_called_once_with("dragon")
        mock_repository.get_monster.assert_called_once_with("dragon")
        
        # Verify API client was NOT called (cache hit)
        mock_api_client.get_monster.assert_not_called()

    def test_get_monster_cache_miss(self, monster_service, mock_repository, mock_api_client):
        # Arrange
        mock_repository.exists_monster.return_value = False  # Monster not in cache
        
        # Mock API response for the monster
        api_response = {
            "index": "dragon",
            "name": "Dragon",
            "url": "/api/monsters/dragon",
            "type": "dragon",
            "size": "huge",
            "hit_points": 256
        }
        mock_api_client.get_monster.return_value = api_response
        
        # Mock successful save to cache
        mock_repository.save_monster.return_value = True
        
        # Act
        result = monster_service.get_monster("dragon")
        
        # Assert
        assert isinstance(result, CacheResult)
        assert result.is_cached is False
        assert result.source == "api"
        assert result.data.index == "dragon"
        assert result.data.name == "Dragon"
        assert result.data.data["type"] == "dragon"
        assert result.data.data["size"] == "huge"
        assert result.data.data["hit_points"] == 256
        
        # Verify repository methods were called
        mock_repository.exists_monster.assert_called_once_with("dragon")
        mock_repository.save_monster.assert_called_once()
        
        # Verify API client was called (cache miss)
        mock_api_client.get_monster.assert_called_once_with("dragon")

    def test_get_monster_api_not_found_error(self, monster_service, mock_repository, mock_api_client):
        # Arrange
        mock_repository.exists_monster.return_value = False  # Monster not in cache
        
        # Mock API to return None (simulating not found)
        mock_api_client.get_monster.return_value = None
        
        # Act & Assert - Should raise ServiceError when API returns None
        with pytest.raises(ServiceError) as exc_info:
            monster_service.get_monster("dragon")
        
        # Verify the error message
        assert "Failed to get monster: Monster not found in external API: dragon" in str(exc_info.value)
        
        # Verify repository methods were called
        mock_repository.exists_monster.assert_called_once_with("dragon")
        
        # Verify API was called
        mock_api_client.get_monster.assert_called_once_with("dragon")
        
        # Verify repository save was NOT attempted (since API failed)
        mock_repository.save_monster.assert_not_called()

    def test_get_monster_with_whitespace_key(self, monster_service, mock_repository, mock_api_client):
        # Arrange - Whitespace-only monster index
        whitespace_index = "   "
        
        # Act & Assert - Should raise ValidationError for whitespace-only key
        with pytest.raises(ValidationError) as exc_info:
            monster_service.get_monster(whitespace_index)
        
        # Verify the error message
        assert "Monster index must be a non-empty string" in str(exc_info.value)
        
        # Verify repository was NOT called (validation failed before reaching repository)
        mock_repository.exists_monster.assert_not_called()
        mock_repository.get_monster.assert_not_called()
        
        # Verify API was NOT called (validation failed before reaching API)
        mock_api_client.get_monster.assert_not_called()

    def test_get_monster_save_to_cache_failure(self, monster_service, mock_repository, mock_api_client):
        # Arrange - Cache miss, API returns data, but save fails
        mock_repository.exists_monster.return_value = False  # Monster not in cache
        
        # Mock API response for the monster
        api_response = {
            "index": "dragon",
            "name": "Dragon",
            "url": "/api/monsters/dragon",
            "type": "dragon",
            "size": "huge"
        }
        mock_api_client.get_monster.return_value = api_response
        
        # Mock failed save to cache
        mock_repository.save_monster.return_value = False
        
        # Act
        result = monster_service.get_monster("dragon")
        
        # Assert - Should still return the monster even if cache save fails
        assert isinstance(result, CacheResult)
        assert result.is_cached is False
        assert result.source == "api"
        assert result.data.index == "dragon"
        assert result.data.name == "Dragon"
        
        # Verify repository methods were called
        mock_repository.exists_monster.assert_called_once_with("dragon")
        mock_repository.save_monster.assert_called_once()
        
        # Verify API client was called (cache miss)
        mock_api_client.get_monster.assert_called_once_with("dragon")

    def test_get_monster_api_returns_malformed_data(self, monster_service, mock_repository, mock_api_client):
        # Arrange - Cache miss, API returns malformed data
        mock_repository.exists_monster.return_value = False  # Monster not in cache
        
        # Mock API response with missing required fields
        malformed_api_response = {
            "name": "Dragon",  # Missing 'index' field
            "url": "/api/monsters/dragon"
            # Missing 'type' and other fields
        }
        mock_api_client.get_monster.return_value = malformed_api_response
        
        # Mock successful save to cache
        mock_repository.save_monster.return_value = True
        
        # Act
        result = monster_service.get_monster("dragon")
        
        # Assert - Should handle malformed data gracefully
        assert isinstance(result, CacheResult)
        assert result.is_cached is False
        assert result.source == "api"
        assert result.data.index == "dragon"  # Should use the search key as fallback
        assert result.data.name == "Dragon"
        assert result.data.url == "/api/monsters/dragon"
        
        # Verify repository methods were called
        mock_repository.exists_monster.assert_called_once_with("dragon")
        mock_repository.save_monster.assert_called_once()
        
        # Verify API client was called (cache miss)
        mock_api_client.get_monster.assert_called_once_with("dragon")
