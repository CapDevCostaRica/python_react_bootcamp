"""
Validation for monster API requests.
"""
from typing import Dict, Any

class MonsterValidator:
    
    def validate_monster_request(self, data: Dict[str, Any]) -> bool:
        """
        Validate POST /get request.
        Expected: {"monster_index": "index"}
        """
        return (
            isinstance(data, dict) and
            data.get('monster_index') and
            isinstance(data.get('monster_index'), str)
        )
    
    def validate_monster_list_request(self, data: Dict[str, Any]) -> bool:
        """
        Validate POST /list request.
        Expected: {"resource": "monsters"}
        """
        return (
            isinstance(data, dict) and
            data.get('resource') == 'monsters'
        ) 