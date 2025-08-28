from marshmallow import Schema, fields

class MonsterListRequestSchema(Schema):
    resource = fields.Str(required=False)