from marshmallow import Schema, fields, validate

class UsageSchema(Schema):
    type = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.OneOf(["at will", "per day", "recharge after rest", "recharge on roll"])
    )
    rest_types = fields.List(fields.Str(), required=False, allow_none=True)
    times = fields.Int(required=False, allow_none=True)
    dice = fields.Str(required=False, allow_none=True)
    min_value = fields.Int(required=False, allow_none=True)

class APIReferenceSchema(Schema):
    index = fields.Str(required=False, allow_none=True)
    name = fields.Str(required=False, allow_none=True)
    url = fields.Str(required=False, allow_none=True)
    updated_at = fields.Str(required=False, allow_none=True)

class ChoiceSchema(Schema):
    desc = fields.String(required=False, allow_none=True)
    type = fields.String(required=False, allow_none=True)
    choose = fields.Integer(required=False, allow_none=True)
    from_ = fields.Raw(required=False, allow_none=True, data_key="from")

class ActionDetailSchema(Schema):
    action_name = fields.String(required=False, allow_none=True)
    type = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf(["melee", "ranged", "ability", "magic"])
    )
    count = fields.Integer(required=False, allow_none=True)
    desc = fields.String(required=False, allow_none=True)
    type = fields.String(required=False, allow_none=True)
    choose = fields.Integer(required=False, allow_none=True)
    from_ = fields.Raw(required=False, allow_none=True, data_key="from")

class DCSchema(Schema):
    dc_type = fields.Nested(APIReferenceSchema, required=False, allow_none=True)
    dc_value = fields.Int(required=False, allow_none=True)
    success_type = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.OneOf(["none", "half", "other"])
    )

class DamageSchema(Schema):
    damage_dice = fields.Str(required=False, allow_none=True)
    damage_type = fields.Nested(APIReferenceSchema, required=False, allow_none=True)
    dc = fields.Nested(DCSchema, required=False, allow_none=True)
    from_ = fields.Raw(required=False, allow_none=True, data_key="from")
    desc = fields.String(required=False, allow_none=True)
    type = fields.String(required=False, allow_none=True)
    choose = fields.Integer(required=False, allow_none=True)

class AttackSchema(Schema):
    name = fields.Str(required=False, allow_none=True)
    dc = fields.Nested(DCSchema, required=False, allow_none=True)
    damage = fields.List(fields.Nested(DamageSchema), required=False, allow_none=True)

class ActionsSchema(Schema):
    name = fields.String(required=False, allow_none=True)
    desc = fields.String(required=False, allow_none=True)
    action_options = fields.Nested(ChoiceSchema, required=False, allow_none=True)
    actions = fields.List(fields.Nested(ActionDetailSchema), required=False, allow_none=True)
    options = fields.Nested(ChoiceSchema, required=False, allow_none=True)
    multiattack_type = fields.String(required=False, allow_none=True)
    attack_bonus = fields.Integer(required=False, allow_none=True)
    dc = fields.Nested(DCSchema, required=False, allow_none=True)
    attacks = fields.List(fields.Nested(AttackSchema), required=False, allow_none=True)
    damage = fields.List(fields.Nested(DamageSchema), required=False, allow_none=True)
    usage = fields.Nested(UsageSchema, required=False, allow_none=True)

class ProficiencySchema(Schema):
    value = fields.Integer(required=False, allow_none=True)
    proficiency = fields.Nested(APIReferenceSchema, required=False, allow_none=True)

class SpeedSchema(Schema):
    walk = fields.Str(required=False, allow_none=True)
    burrow = fields.Str(required=False, allow_none=True)
    climb = fields.Str(required=False, allow_none=True)
    fly = fields.Str(required=False, allow_none=True)
    swim = fields.Str(required=False, allow_none=True)

class SensesSchema(Schema):
    passive_perception = fields.Int(required=False, allow_none=True)
    blindsight = fields.Str(required=False, allow_none=True)
    darkvision = fields.Str(required=False, allow_none=True)
    tremorsense = fields.Str(required=False, allow_none=True)
    truesight = fields.Str(required=False, allow_none=True)
class SpellSchema(Schema):
    name = fields.Str(required=False, allow_none=True)
    level = fields.Int(required=False, allow_none=True)
    url = fields.Str(required=False, allow_none=True)
    usage = fields.Nested(UsageSchema, required=False, allow_none=True)

class SpellcastingSchema(Schema):
    level = fields.Int(required=False, allow_none=True)
    ability = fields.Nested(APIReferenceSchema, required=False, allow_none=True)
    dc = fields.Int(required=False, allow_none=True)
    modifier = fields.Int(required=False, allow_none=True)
    components_required = fields.List(fields.Str(), required=False, allow_none=True)
    school = fields.Str(required=False, allow_none=True)
    slots = fields.Dict(required=False, allow_none=True)
    spells = fields.List(fields.Nested(SpellSchema), required=False, allow_none=True)

class SpecialAbilitySchema(Schema):
    name = fields.Str(required=False, allow_none=True)
    desc = fields.Str(required=False, allow_none=True)
    attack_bonus = fields.Int(required=False, allow_none=True)
    damage = fields.List(fields.Nested(DamageSchema), required=False, allow_none=True)
    dc = fields.Nested(DCSchema, required=False, allow_none=True)
    spellcasting = fields.Nested(SpellcastingSchema, required=False, allow_none=True)
    usage = fields.Nested(UsageSchema, required=False, allow_none=True)

class ArmorClassSchema(Schema):
    type = fields.String(required=False, allow_none=True)
    value = fields.Integer(required=False, allow_none=True)
    armor = fields.List(fields.Nested(APIReferenceSchema), required=False, allow_none=True)

class MonsterSchema(Schema):
    index = fields.String(required=False, allow_none=True)
    name = fields.String(required=False, allow_none=True)
    url = fields.String(required=False, allow_none=True)
    updated_at = fields.String(required=False, allow_none=True)
    desc = fields.String(required=False, allow_none=True)
    charisma = fields.Integer(required=False, allow_none=True)
    constitution = fields.Integer(required=False, allow_none=True)
    dexterity = fields.Integer(required=False, allow_none=True)
    intelligence = fields.Integer(required=False, allow_none=True)
    strength = fields.Integer(required=False, allow_none=True)
    wisdom = fields.Integer(required=False, allow_none=True)
    image = fields.String(required=False, allow_none=True)
    size = fields.String(
        required=False,
        allow_none=True,
        validate=validate.OneOf(["Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan"])
    )
    type = fields.String(required=False, allow_none=True)
    subtype = fields.String(required=False, allow_none=True)
    alignment = fields.String(required=False, allow_none=True)
    armor_class = fields.List(fields.Nested(ArmorClassSchema), required=False, allow_none=True)
    hit_points = fields.Integer(required=False, allow_none=True)
    hit_dice = fields.String(required=False, allow_none=True)
    hit_points_roll = fields.String(required=False, allow_none=True)
    actions = fields.List(fields.Nested(ActionsSchema), required=False, allow_none=True)
    legendary_actions = fields.List(fields.Nested(ActionsSchema), required=False, allow_none=True)
    challenge_rating = fields.Float(
        required=False,
        allow_none=True,
        validate=validate.Range(max=21)
    )
    proficiency_bonus = fields.Int(
        required=False,
        allow_none=True,
        validate=validate.Range(min=2, max=9)
    )
    condition_immunities = fields.List(fields.Nested(APIReferenceSchema), required=False, allow_none=True)
    damage_immunities = fields.List(fields.String(), required=False, allow_none=True)
    damage_resistances = fields.List(fields.String(), required=False, allow_none=True)
    damage_vulnerabilities = fields.List(fields.String(), required=False, allow_none=True)
    forms = fields.List(fields.Nested(APIReferenceSchema), required=False, allow_none=True)
    languages = fields.String(required=False, allow_none=True)
    proficiencies = fields.List(fields.Nested(ProficiencySchema), required=False, allow_none=True)
    reactions = fields.List(fields.Nested(ActionsSchema), required=False, allow_none=True)
    senses = fields.Nested(SensesSchema, required=False, allow_none=True)
    special_abilities = fields.List(fields.Nested(SpecialAbilitySchema), required=False, allow_none=True)
    speed = fields.Nested(SpeedSchema, required=False, allow_none=True)
    xp = fields.Integer(required=False, allow_none=True)
    