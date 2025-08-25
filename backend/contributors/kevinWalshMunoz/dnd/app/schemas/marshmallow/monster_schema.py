from marshmallow import Schema, fields, ValidationError

class MonsterIndexValidation(fields.Field):
    def _deserialize(self, value, attr, data):
        if not isinstance(value, str):
            raise ValidationError("Monster index is required and cannot be empty")
        if not value.strip():
            raise ValidationError("Monster index is required and cannot be empty")
        return value

class MonsterWordValidation(fields.Field):
    def _deserialize(self, value, attr, data):
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        if value != "monsters":
            raise ValidationError("Payload must be exactly 'monsters'")
        return value

class MonsterRequestSchema(Schema):
    monster_index = MonsterIndexValidation(required=True)
    
class MonsterListRequestSchema(Schema):
    resource = MonsterWordValidation(required=True)