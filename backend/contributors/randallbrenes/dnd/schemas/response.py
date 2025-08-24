import os
import sys
from marshmallow import Schema, fields
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from monster import MonsterSchema

class ListResponse(Schema):
    index = fields.String(required=True)
    name = fields.String(required=True)
    url = fields.String(required=True)

class ResponseListSchema(Schema):
    count = fields.Integer()
    results = fields.List(fields.Nested(ListResponse))

    @staticmethod
    def empty():
        return {"count": 0, "results": []}

class ResponseGetSchema(MonsterSchema):
    pass

class Response(Schema):
    error = fields.String(required=False)
    code = fields.Integer()
    monster = fields.Nested(ResponseGetSchema, required=False)
    list = fields.Nested(ResponseListSchema, required=False)
