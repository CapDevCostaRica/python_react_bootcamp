from marshmallow import Schema, fields

class LoginRequestSchema(Schema):
    username = fields.String(required=True)

class UserSchema(Schema):
    id = fields.Integer(required=True)
    username = fields.String(required=True)
    role = fields.String(required=True)