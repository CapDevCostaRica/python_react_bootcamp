from marshmallow import Schema, ValidationError, fields, validate

class FiltersField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, dict):
            return [value]
        elif isinstance(value, list) and all(isinstance(i, dict) for i in value):
            return value
        else:
            raise ValidationError("filters must be a dict or a list of dicts")
        
class RequestFindSchema(Schema):
    filters = FiltersField(required=True)
    select_fields = fields.String(required=False)

class DataSchema(Schema):
    total = fields.Integer(required=True)
    results = fields.List(fields.String(), required=True)

class ResponseFindSchema(Schema):
    success = fields.Boolean(required=True)
    message = fields.String(required=False)
    data = fields.Nested(DataSchema, required=False)
    code = fields.Integer(required=True)

class ResponseDictSchema(Schema):
    success = fields.Boolean(required=True)
    message = fields.String(required=False)
    data = fields.Dict(required=False)
    code = fields.Integer(required=True)

class ResponseListSchema(Schema):
    success = fields.Boolean(required=True)
    message = fields.String(required=False)
    data = fields.List(fields.String(), required=False)
    code = fields.Integer(required=True)

class ResponseStringGroupSchema(Schema):
    success = fields.Boolean(required=True)
    message = fields.String(required=False)
    data = fields.String(required=False)
    code = fields.Integer(required=True)

class ResponseIntGroupSchema(Schema):
    success = fields.Boolean(required=True)
    message = fields.String(required=False)
    data = fields.Integer(required=False)
    code = fields.Integer(required=True)

class WeightGroupFilter(Schema):
    weight = fields.Integer(required=True)

class WeightGroupSchema(Schema):
    filters = fields.Nested(WeightGroupFilter, required=False)

class FoodGroupFilter(Schema):
    food = fields.List(fields.String(), required=True)

class FoodGroupSchema(Schema):
    filters = fields.Nested(FoodGroupFilter, required=False)
