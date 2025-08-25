"""
This module initializes the Marshmallow schemas package
"""

# Import schemas to facilitate access from outside
from app.schemas.marshmallow.monster_schema import MonsterRequestSchema

# Explicitly export the schemas
__all__ = ['MonsterRequestSchema', 'MonsterListRequestSchema', 'MonsterListResponseModelSchema', 'DetailedMonsterSchema', 'MonsterDetailResponseSchema']
