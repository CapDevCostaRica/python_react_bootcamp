from marshmallow import Schema, fields , validate

class MonsterSchema_majocr(Schema):
    index = fields.String(required=True, validate=validate.Length(min=1))
    name = fields.String(required=True, validate=validate.Length(min=1))
    data = fields.Dict(required=True)