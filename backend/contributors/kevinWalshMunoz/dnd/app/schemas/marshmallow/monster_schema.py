from marshmallow import Schema, fields, ValidationError

class MonsterIndexValidation(fields.Field):
    def _deserialize(self, value, attr, data):
        if not isinstance(value, str):
            raise ValidationError("Monster index is required and cannot be empty")
        if not value.strip():
            raise ValidationError("Monster index is required and cannot be empty")
        return value

class MonsterWordValidation(fields.Field):
    def _deserialize(self, value, attr, data):
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        if value != "monsters":
            raise ValidationError("Payload must be exactly 'monsters'")
        return value

class MonsterRequestSchema(Schema):
    monster_index = MonsterIndexValidation(required=True)

#Response Schema
    
class MonsterListRequestSchema(Schema):
    resource = MonsterWordValidation(required=True)

class MonsterSchema(Schema):
    index = fields.String(dump_only=True)
    name = fields.String()
    url = fields.String()

class MonsterListResponseModelSchema(Schema):
    count = fields.Integer()
    results = fields.List(fields.Nested(MonsterSchema))


#dnd api response

class ProficiencySchema(Schema):
    value = fields.Integer()
    proficiency = fields.Dict(keys=fields.String(), values=fields.Field())

class DamageSchema(Schema):
    damage_type = fields.Dict(keys=fields.String(), values=fields.Field())
    damage_dice = fields.String(allow_none=True)

class DCSchema(Schema):
    dc_type = fields.Dict(keys=fields.String(), values=fields.Field())
    dc_value = fields.Integer()
    success_type = fields.String()

class UsageSchema(Schema):
    type = fields.String()
    times = fields.Integer(allow_none=True)
    dice = fields.String(allow_none=True)
    min_value = fields.Integer(allow_none=True)
    rest_types = fields.List(fields.String(), allow_none=True)

class SpellSchema(Schema):
    name = fields.String()
    level = fields.Integer()
    url = fields.String()
    notes = fields.String(allow_none=True)
    usage = fields.Nested(UsageSchema, allow_none=True)

class SpellcastingSchema(Schema):
    level = fields.Integer()
    ability = fields.Dict(keys=fields.String(), values=fields.Field())
    dc = fields.Integer()
    modifier = fields.Integer()
    components_required = fields.List(fields.String())
    school = fields.String()
    slots = fields.Dict(keys=fields.String(), values=fields.Integer())
    spells = fields.List(fields.Nested(SpellSchema))

class AbilitySchema(Schema):
    name = fields.String()
    desc = fields.String()
    usage = fields.Nested(UsageSchema, allow_none=True)
    damage = fields.List(fields.Nested(DamageSchema))
    dc = fields.Nested(DCSchema, allow_none=True)
    actions = fields.List(fields.Dict(), allow_none=True)
    options = fields.Dict(keys=fields.String(), values=fields.Field(), allow_none=True)
    attack_bonus = fields.Integer(allow_none=True)
    multiattack_type = fields.String(allow_none=True)
    spellcasting = fields.Nested(SpellcastingSchema, allow_none=True)

class ArmorClassSchema(Schema):
    type = fields.String()
    value = fields.Integer()
    spell = fields.Dict(keys=fields.String(), values=fields.Field(), allow_none=True)

class SpeedSchema(Schema):
    walk = fields.String(allow_none=True)
    fly = fields.String(allow_none=True)
    swim = fields.String(allow_none=True)
    burrow = fields.String(allow_none=True)
    climb = fields.String(allow_none=True)
    hover = fields.Boolean(allow_none=True)

class SensesSchema(Schema):
    darkvision = fields.String(allow_none=True)
    blindsight = fields.String(allow_none=True)
    tremorsense = fields.String(allow_none=True)
    truesight = fields.String(allow_none=True)
    passive_perception = fields.Integer(allow_none=True)

class DetailedMonsterSchema(Schema):
    """Schema for the full monster details including all attributes"""
    id = fields.Integer(dump_only=True)
    index = fields.String()
    name = fields.String()
    desc = fields.String(allow_none=True)
    size = fields.String()
    type = fields.String()
    subtype = fields.String(allow_none=True)
    alignment = fields.String()
    
    armor_class = fields.List(fields.Nested(ArmorClassSchema))
    hit_points = fields.Integer()
    hit_dice = fields.String()
    hit_points_roll = fields.String()
    speed = fields.Nested(SpeedSchema)
    
    strength = fields.Integer()
    dexterity = fields.Integer()
    constitution = fields.Integer()
    intelligence = fields.Integer()
    wisdom = fields.Integer()
    charisma = fields.Integer()
    
    proficiencies = fields.List(fields.Nested(ProficiencySchema))
    damage_vulnerabilities = fields.List(fields.String())
    damage_resistances = fields.List(fields.String())
    damage_immunities = fields.List(fields.String())
    condition_immunities = fields.List(fields.Dict())
    
    senses = fields.Nested(SensesSchema)
    languages = fields.String()
    challenge_rating = fields.Float()  # Using Float to handle fractions like 1/4, 1/2
    proficiency_bonus = fields.Integer()
    xp = fields.Integer()
    
    special_abilities = fields.List(fields.Nested(AbilitySchema))
    actions = fields.List(fields.Nested(AbilitySchema))
    legendary_actions = fields.List(fields.Nested(AbilitySchema))
    reactions = fields.List(fields.Nested(AbilitySchema))
    forms = fields.List(fields.Dict())
    
    image = fields.String()
    url = fields.String()
    updated_at = fields.DateTime()

class MonsterDetailResponseSchema(DetailedMonsterSchema):
    """Schema for monster detail response that directly uses the DetailedMonsterSchema"""
    pass
