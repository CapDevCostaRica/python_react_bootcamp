from marshmallow import Schema, fields

class LoginSchema(Schema):
    username = fields.String(required=True)
