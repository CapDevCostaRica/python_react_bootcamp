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

#Response Schema
    
class MonsterListRequestSchema(Schema):
    resource = MonsterWordValidation(required=True)

class MonsterSchema(Schema):
    index = fields.String(dump_only=True)
    name = fields.String()
    url = fields.String()

class MonsterListResponseModelSchema(Schema):
    count = fields.Integer()
    results = fields.List(fields.Nested(MonsterSchema))