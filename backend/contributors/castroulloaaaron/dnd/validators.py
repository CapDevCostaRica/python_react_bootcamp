from marshmallow import Schema, fields, validate


class InputGetValidator(Schema):
    monster_index = fields.String(required=True, validate=lambda s: bool(s and not s.isspace(
    )), error_messages={'validator_failed': 'monster_index cannot be empty or whitespace only'})


input_get_schema = InputGetValidator()


class OutputGetValidator(Schema):
    class Meta:
        unknown = 'EXCLUDE'


output_get_schema = OutputGetValidator()


class InputListValidator(Schema):
    resource = fields.String(required=True, validate=lambda s: bool(s and not s.isspace(
    )), error_messages={'validator_failed': 'monster_index cannot be empty or whitespace only'})


input_list_schema = InputListValidator()


class OutputListValidator(Schema):
    class Meta:
        type_: 'list'
        unknown = 'EXCLUDE'


output_list_schema = OutputListValidator(many=True)
