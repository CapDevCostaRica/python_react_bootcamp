from services.telemetry import setupLogger
from marshmallow import Schema, fields,validates, INCLUDE, ValidationError

logger = setupLogger()

class MonstersCrisariasSchema(Schema):
    index = fields.Str(required=True)
    name = fields.Str(required=True)
    url = fields.Str(required=True)

    class Meta:
        unknown = INCLUDE  # Include unknown fields (optional properties not defined in the schema)
        
class ListMonstersSchema(Schema):
    resource = fields.Str(
        required=True
    )
    
    @validates('resource')
    def validate_resource(self, value, data_key: str):
        if not value or not value.strip():
            raise ValidationError(f'{data_key} is required.')
        if data_key == 'resource' and value != 'monsters':
            raise ValidationError('Only monsters resource is valid.')

class GetMonsterSchema(Schema):
    monster_index = fields.Str(required=True)

    @validates('monster_index')
    def validate_monster_index(self, value, data_key: str):
        if not value or not value.strip():
            raise ValidationError(f'{data_key} is required.')
