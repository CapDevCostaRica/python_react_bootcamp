"""
Unit tests for MonsterService class
"""
import pytest
from unittest.mock import Mock
from src.application.service import MonsterService
from src.domain.entities.monster import Monster
from src.domain.entities.monster_list import MonsterList
from src.domain.entities.cache_result import CacheResult


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
