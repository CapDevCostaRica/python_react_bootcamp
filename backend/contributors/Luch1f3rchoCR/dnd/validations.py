from marshmallow import Schema, fields, validate, ValidationError

class ListRequestSchema(Schema):
    resource = fields.String(
        required=True,
        validate=validate.OneOf(["monsters"])
    )

class DetailRequestSchema(Schema):
    monster_index = fields.String(required=True)

class HandlerRequestSchema(Schema):
    resource = fields.String(validate=validate.OneOf(["monsters"]))
    monster_index = fields.String()

    # Validamos que venga uno u otro, no ambos ni ninguno
    def validate_any(self, data, **kwargs):
        if ("resource" in data) == ("monster_index" in data):
            raise ValidationError(
                "Send exactly one of: resource OR monster_index."
            )
        return data
