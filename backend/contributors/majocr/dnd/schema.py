from marshmallow import Schema, ValidationError, fields , validate, validates_schema

class MonsterSchema_majocr(Schema):
    index = fields.String(required=True, validate=validate.Length(min=1))
    name = fields.String(required=True, validate=validate.Length(min=1))
    data = fields.Dict(required=True)

class MonsterListSchema_majocr(Schema):
    index = fields.String(required=True, validate=validate.Length(min=1))
    name = fields.String(required=True, validate=validate.Length(min=1))
    url = fields.String(required=True, validate=validate.Length(min=1))

class MonsterRequestSchema_majocr(Schema):
    monster_index = fields.Str(required=True)

class MonstersListResourceSchema_majocr(Schema):
    resource = fields.Str(required=True)

    @validates_schema
    def validate_monsters_resource(self, data, **kwargs):
        if data.get('resource') != 'monsters':
            raise ValidationError("The 'resource' field must be 'monsters'.")