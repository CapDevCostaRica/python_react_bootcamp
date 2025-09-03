from ..telemetry import logger
from marshmallow import Schema, fields,validates, EXCLUDE, ValidationError

class FilterSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    food = fields.Str()
    family = fields.Str()
    hobby = fields.Str()
    eye_color = fields.Str()
    hair_color = fields.Str()
    age = fields.Int()
    height_cm = fields.Int()
    weight_kg = fields.Int()
    nationality = fields.Str()
    degree = fields.Str()
    institution = fields.Str()

    @validates('age', 'height_cm', 'weight_kg')
    def validate_resource(self, value, data_key: str):
        if not value:
            return True
        if data_key == 'age' and value:
            if value < 0:
                raise ValidationError('Age must be a positive integer.')
        if data_key == 'height_cm' and value:
            if value < 0:
                raise ValidationError('Height must be a positive integer.')
        if data_key == 'weight_kg' and value:
            if value < 0:
                raise ValidationError('Weight must be a positive integer.')
