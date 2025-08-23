from marshmallow import Schema, ValidationError, fields , validate, validates_schema

class MonsterSchema_majocr(Schema):
    index = fields.String(required=True, validate=validate.Length(min=1))
    name = fields.String(required=True, validate=validate.Length(min=1))
    data = fields.Dict(required=True)

    @validates_schema
    def validate_data_structure(self, data, **kwargs):
        monster_data = data.get("data", {})
        if not isinstance(monster_data, dict):
            raise ValidationError({"data": "Must be a dictionary."})
        #Validate presence of essential keys
        required_keys = ["size", "type", "actions"]
        missing = [key for key in required_keys if key not in monster_data or monster_data[key] in [None, "", [], {}]]
        if missing:
            raise ValidationError({"data": f"Missing or empty required keys: {missing}"})
        #Validate 'actions' is a list
        if not isinstance(monster_data["actions"], list):
            raise ValidationError({"data": "'actions' must be a list."})


class MonsterListSchema_majocr(Schema):
    index = fields.String(required=True, validate=validate.Length(min=1))
    name = fields.String(required=True, validate=validate.Length(min=1))
    url = fields.String(required=True, validate=validate.Length(min=1))

class MonsterListOutputSchema_majocr(Schema):
    count = fields.Integer(required=True)
    results = fields.List(fields.Nested(MonsterListSchema_majocr), required=True)

class MonsterRequestSchema_majocr(Schema):
    monster_index = fields.Str(required=True)

class MonstersListResourceSchema_majocr(Schema):
    resource = fields.Str(required=True)

    @validates_schema
    def validate_monsters_resource(self, data, **kwargs):
        if data.get('resource') != 'monsters':
            raise ValidationError("The 'resource' field must be 'monsters'.")
