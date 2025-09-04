from marshmallow import Schema, fields, validate, ValidationError

class BaseResponseSchema(Schema):
    success = fields.Bool(required=True)
    error = fields.Str(allow_none=True)


class PeopleFindRequestSchema(Schema):
    food = fields.Str(allow_none=True, validate=validate.Length(max=100))
    family = fields.Str(allow_none=True, validate=validate.Length(max=100))
    hobby = fields.Str(allow_none=True, validate=validate.Length(max=100))
    eye_color = fields.Str(allow_none=True, validate=validate.Length(max=50))
    hair_color = fields.Str(allow_none=True, validate=validate.Length(max=50))
    age = fields.Int(allow_none=True, validate=validate.Range(min=0, max=150))
    height_cm = fields.Float(allow_none=True, validate=validate.Range(min=0, max=300))
    weight_kg = fields.Float(allow_none=True, validate=validate.Range(min=0, max=500))
    nationality = fields.Str(allow_none=True, validate=validate.Length(max=100))
    degree = fields.Str(allow_none=True, validate=validate.Length(max=100))
    institution = fields.Str(allow_none=True, validate=validate.Length(max=200))


class PeopleFindResponseSchema(BaseResponseSchema):
    data = fields.Dict(required=True)


class SushiRamenResponseSchema(BaseResponseSchema):
    data = fields.Int(required=True)
    
class MostCommonFoodResponseSchema(BaseResponseSchema):
    data = fields.Str(required=True)


class TopHobbiesResponseSchema(BaseResponseSchema):
    data = fields.List(fields.Str(), required=True)


class AvgWeightHairResponseSchema(BaseResponseSchema):
    data = fields.Dict(keys=fields.Str(), values=fields.Float(), required=True)


class AvgWeightNationalityHairResponseSchema(BaseResponseSchema):
    data = fields.Dict(keys=fields.Str(), values=fields.Float(), required=True)


class TopOldestNationalityResponseSchema(BaseResponseSchema):
    data = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()), required=True)


class AvgHeightNationalityGeneralResponseSchema(BaseResponseSchema):
    data = fields.Dict(required=True)


def validate_request_data(schema_class, data):
    try:
        schema = schema_class()
        validated_data = schema.load(data)
        return True, validated_data, None
    except ValidationError as e:
        return False, None, e.messages


def validate_response_data(schema_class, data):
    try:
        schema = schema_class()
        validated_data = schema.dump(data)
        return True, validated_data, None
    except ValidationError as e:
        return False, None, e.messages
