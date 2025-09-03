from marshmallow import Schema, ValidationError, fields , validate, validates_schema


class PeopleSchema_majocr(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True, validate=validate.Length(min=1))
    age = fields.Integer(required=True, validate=validate.Range(min=0))
    eye_color = fields.String(required=True, validate=validate.Length(min=1))
    hair_color = fields.String(required=True, validate=validate.Length(min=1))
    height_cm = fields.Float(required=True, validate=validate.Range(min=0))
    weight_kg = fields.Float(required=True, validate=validate.Range(min=1))
    nationality = fields.String(required=True, validate=validate.Length(min=1))

class StudySchema_majocr(Schema):
    person_id = fields.Integer(required=True)
    degree = fields.String(required=True, validate=validate.Length(min=1))
    institution = fields.String(required=True, validate=validate.Length(min=1))


class FamilySchema_majocr(Schema):
    person_id = fields.Integer(required=True)
    relation = fields.String(required=True)
    name = fields.String(required=True, validate=validate.Length(min=1))

class HobbySchema_majocr(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))

class PersonHobbyAssociationSchema_majocr(Schema):
    person_id = fields.Integer(required=True)
    hobby_id = fields.Integer(required=True)

class FoodSchema_majocr(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))    

class PersonFoodAssociationSchema_majocr(Schema):
    person_id = fields.Integer(required=True)
    food_id = fields.Integer(required=True)

class PeopleDataSchema(Schema):
    total = fields.Integer(required=True)
    results = fields.List(fields.String(), required=True)

class PeopleResponseSchema(Schema):
    success = fields.Boolean(required=True)
    data = fields.Nested(PeopleDataSchema, required=True)