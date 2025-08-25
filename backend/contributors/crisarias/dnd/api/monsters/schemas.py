from services.telemetry import setupLogger
from marshmallow import Schema, fields, ValidationError, validates

logger = setupLogger()

class MonstersCrisariasSchema(Schema):
    index = fields.Str(required=True)
    name = fields.Str(required=True)
    url = fields.Str(required=True)

    # @validates('id')
    # def validate_id(self, value):
    #     if not value.strip():
    #         raise ValidationError("ID must not be empty or whitespace.")

    # @validates('body')
    # def validate_body(self, value):
    #     if not isinstance(value, dict):
    #         raise ValidationError("Body must be a valid JSON object.")
        
class ListMonstersSchema(Schema):
    resource = fields.Str(required=True)

    # @validates('resource')
    # def validate_resource(self, value):
    #     logger.info(f"Validating resource: {value}")
    #     if value != "monsters":
    #         raise ValidationError("Resource type not supportted.")
        
class GetMonsterSchema(Schema):
    monster_index = fields.Str(required=True)

    # @validates('monster_index')
    # def validate_index(self, value):
    #     if value < 0:
    #         raise ValidationError("monster_index must be a non-negative integer")
