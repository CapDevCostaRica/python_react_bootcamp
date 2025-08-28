"""
Validation and serialization using Marshmallow schemas.
"""
from typing import Dict, Any
from .schemas import (
    MonsterRequestSchema,
    MonsterListRequestSchema,
    MonsterResponseSchema,
    MonsterListResponseSchema
)


class MonsterValidator:
    """
    Handles request validation and response serialization using Marshmallow schemas.
    """
    
    def __init__(self):
        self.monster_request_schema = MonsterRequestSchema()
        self.monster_list_request_schema = MonsterListRequestSchema()
        self.monster_response_schema = MonsterResponseSchema()
        self.monster_list_response_schema = MonsterListResponseSchema()
    
    def validate_monster_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate POST /get request using Marshmallow schema.
        Expected: {"monster_index": "index"}
        """
        return self.monster_request_schema.load(data)
    
    def validate_monster_list_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate POST /list request using Marshmallow schema.
        Expected: {"resource": "monsters"}
        """
        return self.monster_list_request_schema.load(data)
    
    def serialize_monster_response(self, monster) -> Dict[str, Any]:
        return self.monster_response_schema.dump(monster)
    
    def serialize_monster_list_response(self, monster_list) -> Dict[str, Any]:
        return self.monster_list_response_schema.dump(monster_list) 