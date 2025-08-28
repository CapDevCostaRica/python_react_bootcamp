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
