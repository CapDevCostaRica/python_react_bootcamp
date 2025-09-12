from marshmallow import Schema, fields

class LoginRequestSchema(Schema):
    username = fields.String(required=True)