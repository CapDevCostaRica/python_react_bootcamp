"""
Unit tests for MonsterValidator class
"""
import pytest
from src.application.validators import MonsterValidator


class TestMonsterValidator:
    
    def test_validate_monster_request_valid_data(self):
        # Arrange
        validator = MonsterValidator()
        valid_data = {"monster_index": "dragon"}
        
        # Act
        result = validator.validate_monster_request(valid_data)
        
        # Assert
        assert result == valid_data
        assert result["monster_index"] == "dragon"

    def test_validate_monster_request_invalid_data(self):
        # Arrange
        validator = MonsterValidator()
        invalid_data = {"monster_index": ""}  # Empty string should fail validation
        
        # Act 
        with pytest.raises(Exception) as exc_info:
            validator.validate_monster_request(invalid_data)
        
        # Assert
        error_message = str(exc_info.value)
        assert "monster_index" in error_message.lower()  

    def test_validate_monster_list_request_valid_data(self):
        # Arrange
        validator = MonsterValidator()
        valid_data = {"resource": "monsters"}
        
        # Act
        result = validator.validate_monster_list_request(valid_data)
        
        # Assert
        assert result == valid_data
        assert result["resource"] == "monsters"

    def test_validate_monster_list_request_invalid_data(self):
        # Arrange
        validator = MonsterValidator()
        invalid_data = {"resource": ""}  # Empty string should fail validation
        
        # Act 
        with pytest.raises(Exception) as exc_info:
            validator.validate_monster_list_request(invalid_data)
        
        # Assert
        error_message = str(exc_info.value)
        assert "resource" in error_message.lower()  

    def test_serialize_monster_response(self):
        # Arrange
        from src.domain.entities.monster import Monster
        validator = MonsterValidator()
        monster = Monster(index="dragon", name="Dragon", url="/api/monsters/dragon", data={"type": "dragon"})
        
        # Act
        result = validator.serialize_monster_response(monster)
        
        # Assert
        assert isinstance(result, dict)
        assert result["index"] == "dragon"
        assert result["name"] == "Dragon"
        assert result["url"] == "/api/monsters/dragon"

    def test_serialize_monster_list_response(self):
        # Arrange
        from src.domain.entities.monster import Monster
        from src.domain.entities.monster_list import MonsterList
        validator = MonsterValidator()
        monsters = [
            Monster(index="dragon", name="Dragon", url="/api/monsters/dragon", data={"type": "dragon"}),
            Monster(index="goblin", name="Goblin", url="/api/monsters/goblin", data={"type": "goblin"})
        ]
        monster_list = MonsterList(monsters=monsters, count=2)
        
        # Act
        result = validator.serialize_monster_list_response(monster_list)
        
        # Assert
        assert isinstance(result, dict)
        assert result["count"] == 2
        assert len(result["monsters"]) == 2
        assert result["monsters"][0]["index"] == "dragon"
        assert result["monsters"][1]["index"] == "goblin"
