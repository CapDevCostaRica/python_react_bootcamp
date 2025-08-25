from marshmallow import Schema, fields, validate, ValidationError, INCLUDE, validates_schema

class ListRequestSchema(Schema):
    resource = fields.String(required=True, validate=validate.OneOf(["monsters"]))

class DetailRequestSchema(Schema):
    monster_index = fields.String(required=True)

class HandlerRequestSchema(Schema):
    resource = fields.String(validate=validate.OneOf(["monsters"]))
    monster_index = fields.String()

    @validates_schema
    def validate_any(self, data, **kwargs):
        if ("resource" in data) == ("monster_index" in data):
            raise ValidationError("Send exactly one of: resource OR monster_index.")

class MonsterRefSchema(Schema):
    index = fields.String(required=True)
    name = fields.String(required=True)
    url = fields.String(required=True)

class MonstersListSchema(Schema):
    count = fields.Integer(required=True)
    results = fields.List(fields.Nested(MonsterRefSchema), required=True)

class MonsterDetailSchema(Schema):
    class Meta:
        unknown = INCLUDE
    index = fields.String(required=True)
    name = fields.String(required=True)
    type = fields.String(required=True)