from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from app.models import Person, Food, Hobby, Family, Study

class FindPersonRequestValidator(Schema):
    name = fields.Str(required=False)
    eye_color = fields.Str(required=False)
    hair_color = fields.Str(required=False)
    age = fields.Int(required=False)
    height_cm = fields.Int(required=False)
    weight_kg = fields.Int(required=False)
    nationality = fields.Str(required=False)
    food = fields.Str(required=False)
    hobby = fields.Str(required=False)
    family = fields.Str(required=False)
    degree = fields.Str(required=False)
    institution = fields.Str(required=False)


class FindPersonResponseValidator(Schema):
    total = fields.Int(required=True)
    results = fields.List(fields.String(), required=True)


class PersonSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        load_instance = True
        include_relationships = True