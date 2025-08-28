from marshmallow import Schema, fields

class MonsterRequestSchema(Schema):
    monster_index = fields.Str(required=True)