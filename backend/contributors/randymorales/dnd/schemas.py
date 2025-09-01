from marshmallow import Schema, fields

class RandymoralesMonsterListInputSchema(Schema):
    resource = fields.String(required=True)

class RandymoralesMonsterGetInputSchema(Schema):
    monster_index = fields.String(required=True)

class RandymoralesMonsterListOutputSchema(Schema):
    count = fields.Integer(required=True)
    results = fields.List(fields.Dict(), required=True)

class RandymoralesMonsterGetOutputSchema(Schema):
    index = fields.String(required=True)
    name = fields.String(required=True)
    class Meta:
        unknown = 'INCLUDE'
