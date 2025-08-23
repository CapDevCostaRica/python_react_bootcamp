from marshmallow import Schema, fields, validate


class GetValidator(Schema):
    monster_index = fields.String(required=True, validate=lambda s: bool(s and not s.isspace(
    )), error_messages={'validator_failed': 'monster_index cannot be empty or whitespace only'})


get_schema = GetValidator()


class ListValidator(Schema):
    resource = fields.String(required=True, validate=lambda s: bool(s and not s.isspace(
    )), error_messages={'validator_failed': 'monster_index cannot be empty or whitespace only'})


list_schema = ListValidator()
