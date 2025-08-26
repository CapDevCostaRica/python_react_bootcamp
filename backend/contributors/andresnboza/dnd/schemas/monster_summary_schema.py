from marshmallow import Schema, fields

class MonsterSummarySchema(Schema):
    index = fields.Str()
    name = fields.Str()
    url = fields.Str()
