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
    url   = fields.Method("get_url", dump_only=True)  # ← agrega url calculado

    def get_url(self, obj):
        idx = getattr(obj, "index", None) or (obj.get("index") if isinstance(obj, dict) else None)
        return f"/api/monsters/{idx}" if idx else None

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

class MonsterDetailDataSchema(Schema):
    class Meta:
        unknown = INCLUDE

    index = fields.String(required=True)
    name  = fields.String(required=True)


    size = fields.String(required=False)
    type = fields.String(required=False)
    alignment = fields.String(required=False)
    armor_class = fields.List(fields.Nested(ArmorClassItemSchema), required=False)
    hit_points = fields.Integer(required=False)
    hit_dice = fields.String(required=False)
    hit_points_roll = fields.String(required=False)
    speed = fields.Nested(SpeedSchema, required=False)
    strength = fields.Integer(required=False)
    dexterity = fields.Integer(required=False)
    constitution = fields.Integer(required=False)
    intelligence = fields.Integer(required=False)
    wisdom = fields.Integer(required=False)
    charisma = fields.Integer(required=False)
    proficiencies = fields.List(fields.Nested(ProficiencyEntrySchema), required=False)
    damage_vulnerabilities = fields.List(fields.String(), required=False)
    damage_resistances = fields.List(fields.String(), required=False)
    damage_immunities = fields.List(fields.String(), required=False)
    condition_immunities = fields.List(fields.Nested(ConditionImmunitySchema), required=False)
    senses = fields.Nested(SensesSchema, required=False)
    languages = fields.String(required=False, allow_none=True)
    challenge_rating  = fields.Float(required=False)
    proficiency_bonus = fields.Integer(required=False)
    xp = fields.Integer(required=False)
    actions = fields.List(fields.Nested(ActionSchema), required=False)
    legendary_actions = fields.List(fields.Nested(ActionSchema), required=False)
    reactions = fields.List(fields.Nested(ActionSchema), required=False)
    special_abilities = fields.List(fields.Nested(ActionSchema), required=False)
    image = fields.String(required=False)
    url = fields.String(required=False)
    forms = fields.List(fields.Raw(), required=False)
