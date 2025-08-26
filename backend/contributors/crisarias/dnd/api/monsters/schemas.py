from services.telemetry import setupLogger
from marshmallow import Schema, fields,validates, EXCLUDE, ValidationError

logger = setupLogger()

class MonstersCrisariasSimplifiedSchema(Schema):
    index = fields.Str(required=True)
    name = fields.Str(required=True)
    url = fields.Str(required=True)

class MonstersCrisariasSchema(Schema):
    index = fields.Str(required=True)
    name = fields.Str(required=True)
    url = fields.Str(required=True)
    actions = fields.List(fields.Dict(), allow_none=True)
    alignment = fields.Str()
    armor_class = fields.List(fields.Dict(), allow_none=True)
    challenge_rating = fields.Int()
    charisma = fields.Int()
    condition_immunities = fields.List(fields.Dict(), allow_none=True)
    constitution = fields.Int()
    damage_immunities = fields.List(fields.Dict(), allow_none=True)
    damage_resistances = fields.List(fields.Dict(), allow_none=True)
    damage_vulnerabilities = fields.List(fields.Dict(), allow_none=True)
    dexterity = fields.Int()
    forms = fields.List(fields.Dict(), allow_none=True)
    hit_dice = fields.Str()
    hit_points = fields.Int()
    hit_points_roll = fields.Str()
    image = fields.Str()
    intelligence = fields.Int()
    languages =  fields.Str()
    legendary_actions = fields.List(fields.Dict(), allow_none=True)
    proficiencies = fields.List(fields.Dict(), allow_none=True)
    proficiency_bonus = fields.Int()
    reactions = fields.List(fields.Dict(), allow_none=True)
    senses = fields.Dict(allow_none=True)
    size = fields.Str()
    special_abilities = fields.List(fields.Dict(), allow_none=True)
    speed = fields.Dict(allow_none=True)
    strength = fields.Int()
    type = fields.Str()
    updated_at = fields.DateTime()
    xp = fields.Int()
    wisdom = fields.Int()
    
    @validates('challenge_rating', 'charisma', 'constitution', 'dexterity', 'hit_points', 'intelligence', 'proficiency_bonus', 'strength', 'wisdom', 'xp')
    def validate_attributes(self, value, data_key: str):
        if value is not None and value <= 0:
            raise ValidationError(f'{data_key} must be greater than zero.')

    class Meta:
        unknown = EXCLUDE  # Include unknown fields (optional properties not defined in the schema)
        
class ListMonstersSchema(Schema):
    resource = fields.Str(
        required=True
    )
    
    @validates('resource')
    def validate_resource(self, value, data_key: str):
        if not value or not value.strip():
            raise ValidationError(f'{data_key} is required.')
        if data_key == 'resource' and value != 'monsters':
            raise ValidationError('Only monsters resource is valid.')

class GetMonsterSchema(Schema):
    monster_index = fields.Str(required=True)

    @validates('monster_index')
    def validate_monster_index(self, value, data_key: str):
        if not value or not value.strip():
            raise ValidationError(f'{data_key} is required.')
