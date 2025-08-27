from marshmallow import Schema, fields, validate, ValidationError, post_load


class ListRequestSchema(Schema):
    """Schema for list endpoint request validation."""
    resource = fields.String(required=True, validate=validate.OneOf(['monsters']))
    
    @post_load
    def validate_request(self, data, **kwargs):
        if data['resource'] != 'monsters':
            raise ValidationError('resource must be "monsters"')
        return data


class GetRequestSchema(Schema):
    """Schema for get endpoint request validation."""
    monster_index = fields.String(required=True)
    
    @post_load
    def validate_request(self, data, **kwargs):
        # Validate monster index format (alphanumeric with hyphens)
        index = data['monster_index']
        if not index or not isinstance(index, str):
            raise ValidationError('monster_index must be a non-empty string')
        return data


class MonsterSchema(Schema):
    """Schema for monster data output validation."""
    id = fields.Integer(dump_only=True)
    index = fields.String(required=True)
    name = fields.String(required=True)
    size = fields.String(allow_none=True)
    type = fields.String(allow_none=True)
    subtype = fields.String(allow_none=True)
    alignment = fields.String(allow_none=True)
    armor_class = fields.Raw(allow_none=True)  # Can be complex object
    hit_points = fields.Integer(allow_none=True)
    hit_dice = fields.String(allow_none=True)
    hit_points_roll = fields.String(allow_none=True)
    speed = fields.Raw(allow_none=True)  # Complex object
    strength = fields.Integer(allow_none=True)
    dexterity = fields.Integer(allow_none=True)
    constitution = fields.Integer(allow_none=True)
    intelligence = fields.Integer(allow_none=True)
    wisdom = fields.Integer(allow_none=True)
    charisma = fields.Integer(allow_none=True)
    proficiencies = fields.Raw(allow_none=True)
    damage_vulnerabilities = fields.Raw(allow_none=True)
    damage_resistances = fields.Raw(allow_none=True)
    damage_immunities = fields.Raw(allow_none=True)
    condition_immunities = fields.Raw(allow_none=True)
    senses = fields.Raw(allow_none=True)
    languages = fields.String(allow_none=True)
    challenge_rating = fields.Integer(allow_none=True)
    proficiency_bonus = fields.Integer(allow_none=True)
    xp = fields.Integer(allow_none=True)
    special_abilities = fields.Raw(allow_none=True)
    actions = fields.Raw(allow_none=True)
    legendary_actions = fields.Raw(allow_none=True)
    reactions = fields.Raw(allow_none=True)
    forms = fields.Raw(allow_none=True)
    spellcasting = fields.Raw(allow_none=True)
    image = fields.String(allow_none=True)
    url = fields.String(allow_none=True)


class MonsterListSchema(Schema):
    """Schema for monster list response."""
    count = fields.Integer()
    results = fields.List(fields.Nested(MonsterSchema))


class APIReferenceSchema(Schema):
    """Schema for simple API reference objects."""
    index = fields.String()
    name = fields.String()
    url = fields.String()


class MonsterListItemSchema(Schema):
    """Schema for monster list items (simplified)."""
    index = fields.String()
    name = fields.String()
    url = fields.String()


class MonsterListResponseSchema(Schema):
    """Schema for the list response matching D&D API format."""
    count = fields.Integer()
    results = fields.List(fields.Nested(MonsterListItemSchema))


class ErrorSchema(Schema):
    """Schema for error responses."""
    error = fields.String(required=True)
    message = fields.String()
