from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import MonsterDanrodjim

class ListMonsterResponseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MonsterDanrodjim
        load_instance = True

class ListMonsterRequestSchema(Schema):
    resource = fields.Str(required=True, validate=validate.Equal("monsters", error="Incorrect payload"))

class GetMonsterResponseSchema(Schema):
    data = fields.Dict(required=True)

class GetMonsterRequestSchema(Schema):
    monster_index = fields.Str(required=True, validate=validate.Length(min=1))
