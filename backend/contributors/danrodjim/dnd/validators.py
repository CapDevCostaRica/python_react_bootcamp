from marshmallow import Schema, fields, validate, INCLUDE, post_dump
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models import MonsterDanrodjim

class GetMonsterResponseSchema(Schema):
    class Meta:
        unknown = INCLUDE
    index = fields.Str(required=True)
    name = fields.Str(required=True)
    url = fields.Str(required=True)
    def __init__(self, *args, **kwargs):
        self._context_data = kwargs.pop('raw_data', {})
        super().__init__(*args, **kwargs)

    @post_dump
    def add_unknown(self, data, **kwargs):
        for k, v in self._context_data.items():
            if k not in data:
                data[k] = v
        return data

class ListMonsterResponseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MonsterDanrodjim
        load_instance = True 
    index = auto_field(required=True)
    name = auto_field(required=True)
    url = auto_field(required=True)
    data = fields.Nested(GetMonsterResponseSchema, required=False, allow_none=True)

class ListMonsterRequestSchema(Schema):
    resource = fields.Str(required=True, validate=validate.Equal("monsters", error="Incorrect payload"))

class GetMonsterRequestSchema(Schema):
    monster_index = fields.Str(required=True, validate=validate.Length(min=1))
