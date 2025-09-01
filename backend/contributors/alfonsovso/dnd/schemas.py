from marshmallow import Schema, fields, validate

class ListEventSchema(Schema):
    resource = fields.String(required=True, validate=validate.Equal("monsters"))

class GetEventSchema(Schema):
    monster_index = fields.String(required=True)
