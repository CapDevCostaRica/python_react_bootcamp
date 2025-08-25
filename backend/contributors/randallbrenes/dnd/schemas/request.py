from marshmallow import Schema, fields, validate

class RequestSingleSchema(Schema):
    monster_index = fields.String(required=True)

class RequestAllSchema(Schema):
    resource = fields.String(required=True, validate=validate.Equal("monsters"))
