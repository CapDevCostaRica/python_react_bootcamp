from marshmallow import Schema, ValidationError, fields, validates_schema

class LoginRequestSchema(Schema):
    username = fields.String(required=True)

    @validates_schema
    def validate_schema(self, data, **kwargs):
        if not data.get("username"):
            raise ValidationError("Username is required.")