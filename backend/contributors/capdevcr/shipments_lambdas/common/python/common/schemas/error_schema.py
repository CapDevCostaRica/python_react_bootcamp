from marshmallow import Schema, fields


class ErrorSchema(Schema):
    error = fields.String(required=True)
