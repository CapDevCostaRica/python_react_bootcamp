from marshmallow import schema, fields

class LoginRequestSchema(schema.Schema):
    username = fields.Str(required=True)
