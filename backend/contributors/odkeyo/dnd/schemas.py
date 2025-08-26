from marshmallow import Schema, fields, validate, INCLUDE

class ListInputSchema(Schema):
    resource = fields.String(
        required=True,
        validate=validate.OneOf(["monsters"], error="resource must be 'monsters'")
    )

class GetInputSchema(Schema):
    monster_index = fields.String(
        required=True,
        validate=validate.Length(min=1, error="monster_index is required")
    )

class odkeyo_MonsterListItemSchema(Schema):
    index = fields.String(required=True)
    name  = fields.String(required=True)

class odkeyo_MonsterListSchema(Schema):
    count   = fields.Integer(required=True)
    results = fields.List(fields.Nested(odkeyo_MonsterListItemSchema), required=True)

class odkeyo_MonsterDetailSchema(Schema):
    index = fields.String(required=True)
    name  = fields.String(required=True)
    data  = fields.Dict(required=True)
