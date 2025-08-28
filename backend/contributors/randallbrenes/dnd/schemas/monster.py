from marshmallow import Schema, fields
class MonsterSchema(Schema):
    class Meta:
        unknown = 'EXCLUDE'
    index = fields.Str(required=False, allow_none=True)
    name = fields.Str(required=False, allow_none=True)
    url = fields.Str(required=False, allow_none=True)
    json_data = fields.Dict(required=False, allow_none=True)
