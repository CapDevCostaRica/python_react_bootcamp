from marshmallow import Schema, fields, validate, INCLUDE

class ListEventSchema(Schema):
    resource = fields.String(required=True, validate=validate.Equal("monsters"))

class GetEventSchema(Schema):
    monster_index = fields.String(required=True)

class MonsterIndexItemSchema(Schema):
    index = fields.String(required=True)
    name  = fields.String(required=True)
    url   = fields.String(required=True)

class ListResponseSchema(Schema):
    results = fields.List(fields.Nested(MonsterIndexItemSchema), required=True)

class MonsterDetailSchema(Schema):
    index = fields.String(required=True)
    name  = fields.String(required=True)

    class Meta:
        unknown = INCLUDE

class ErrorSchema(Schema):
    error = fields.String(required=True)
    details = fields.Raw(required=False)
