from marshmallow import Schema, fields, validate, INCLUDE

class ListInputSchema(Schema):
    resource = fields.String(
        required=True,
        validate=validate.OneOf(["monsters"], error="resource must be 'monsters'")
    )

class GetInputSchema(Schema):
    monster_index = fields.String(
        required=True,
        validate=validate.Length(min=1, error="monster_index is required")
    )

class odkeyo_MonsterListItemSchema(Schema):
    index = fields.String(required=True)
    name  = fields.String(required=True)

class odkeyo_MonsterListSchema(Schema):
    count   = fields.Integer(required=True)
    results = fields.List(fields.Nested(odkeyo_MonsterListItemSchema), required=True)

class APIReferenceSchema(Schema):
    index = fields.String(required=True)
    name  = fields.String(required=True)
    url   = fields.String(required=True)

class ArmorClassItemSchema(Schema):
    type  = fields.String(required=True)
    value = fields.Integer(required=True)

class SpeedSchema(Schema):
    walk   = fields.String(required=False)
    climb  = fields.String(required=False)
    fly    = fields.String(required=False)
    swim   = fields.String(required=False)
    burrow = fields.String(required=False)

class ProficiencyEntrySchema(Schema):
    value       = fields.Integer(required=True)
    proficiency = fields.Nested(APIReferenceSchema, required=True)

class SensesSchema(Schema):
    passive_perception = fields.Integer(required=True)

class DamageComponentSchema(Schema):
    damage_type = fields.Nested(APIReferenceSchema, required=True)
    damage_dice = fields.String(required=True)

class MultiattackInnerActionSchema(Schema):
    action_name = fields.String(required=False)
    count       = fields.String(required=False)
    type        = fields.String(required=False)

class ActionSchema(Schema):
    name             = fields.String(required=True)
    desc             = fields.String(required=True)
    attack_bonus     = fields.Integer(required=False, allow_none=True)
    multiattack_type = fields.String(required=False)
    damage           = fields.List(fields.Nested(DamageComponentSchema), required=False)
    actions          = fields.List(fields.Nested(MultiattackInnerActionSchema), required=False)

class ConditionImmunitySchema(Schema):
    index = fields.String(required=True)
    name  = fields.String(required=True)
    url   = fields.String(required=True)

class odkeyo_MonsterDetailSchema(Schema):
    
    index = fields.String(required=True)
    name  = fields.String(required=True)
    size = fields.String(required=True)
    type = fields.String(required=True)
    alignment = fields.String(required=True)
    armor_class = fields.List(fields.Nested(ArmorClassItemSchema), required=True)
    hit_points = fields.Integer(required=True)
    hit_dice = fields.String(required=True)
    hit_points_roll = fields.String(required=True)
    speed = fields.Nested(SpeedSchema, required=True)
    strength = fields.Integer(required=True)
    dexterity = fields.Integer(required=True)
    constitution = fields.Integer(required=True)
    intelligence = fields.Integer(required=True)
    wisdom = fields.Integer(required=True)
    charisma = fields.Integer(required=True)
    proficiencies = fields.List(fields.Nested(ProficiencyEntrySchema), required=True)
    damage_vulnerabilities = fields.List(fields.String(), required=True)
    damage_resistances = fields.List(fields.String(), required=True)
    damage_immunities = fields.List(fields.String(), required=True)
    condition_immunities = fields.List(fields.Nested(ConditionImmunitySchema), required=True)
    senses = fields.Nested(SensesSchema, required=True)
    languages = fields.String(required=True, allow_none=True)
    challenge_rating  = fields.Float(required=True)
    proficiency_bonus = fields.Integer(required=True)
    xp = fields.Integer(required=True)
    actions = fields.List(fields.Nested(ActionSchema), required=True)
    legendary_actions = fields.List(fields.Nested(ActionSchema), required=True)
    reactions = fields.List(fields.Nested(ActionSchema), required=True)
    special_abilities = fields.List(fields.Nested(ActionSchema), required=True)
    image = fields.String(required=False)
    url = fields.String(required=False)
    forms = fields.List(fields.Raw(), required=True)
