from services.telemetry import setupLogger
from marshmallow import Schema, fields, INCLUDE

logger = setupLogger()

class MonstersCrisariasSchema(Schema):
    index = fields.Str(required=True)
    name = fields.Str(required=True)
    url = fields.Str(required=True)

    class Meta:
        unknown = INCLUDE  # Include unknown fields (optional properties not defined in the schema)
        
class ListMonstersSchema(Schema):
    resource = fields.Str(required=True)
        
class GetMonsterSchema(Schema):
    monster_index = fields.Str(required=True)
