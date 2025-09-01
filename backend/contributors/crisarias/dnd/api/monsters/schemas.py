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
    updated_at = fields.Str()
    desc = fields.Str()
    charisma = fields.Int()
    constitution = fields.Int()
    dexterity = fields.Int()
    intelligence = fields.Int()
    strength = fields.Int()
    wisdom = fields.Int()
    image = fields.Str()
    size = fields.Str()
    type = fields.Str()
    subtype = fields.Str()
    alignment = fields.Str()
    armor_class = fields.List(fields.Dict(), allow_none=True)
    hit_points = fields.Int()
    hit_dice = fields.Str()    
    hit_points_roll = fields.Str()
    actions = fields.List(fields.Dict(), allow_none=True)
    legendary_actions = fields.List(fields.Dict(), allow_none=True)
    challenge_rating = fields.Int()
    proficiency_bonus = fields.Int()
    condition_immunities = fields.List(fields.Dict(), allow_none=True)
    damage_immunities = fields.List(fields.String(), allow_none=True)
    damage_resistances = fields.List(fields.String(), allow_none=True)
    damage_vulnerabilities = fields.List(fields.String(), allow_none=True)
    forms = fields.List(fields.Dict(), allow_none=True)
    languages =  fields.Str()
    proficiencies = fields.List(fields.Dict(), allow_none=True)
    reactions = fields.List(fields.Dict(), allow_none=True)    
    senses = fields.Dict(allow_none=True)
    special_abilities = fields.List(fields.Dict(), allow_none=True)
    dc = fields.Dict()
    spellcasting = fields.Dict()
    usage  = fields.Dict()
    speed = fields.Dict()
    xp = fields.Int()

    @validates('size', 'challenge_rating', 'proficiency_bonus')
    def validate_resource(self, value, data_key: str):
        if not value:
            return True
        if data_key == 'size' and value:  # Only validate if value exists
            valid_sizes = ['Tiny', 'Small', 'Medium', 'Large', 'Huge', 'Gargantuan']
            if value not in valid_sizes:
                raise ValidationError(f'Size must be one of: {", ".join(valid_sizes)}')
        if data_key == 'challenge_rating' and value:
            if value > 21:
                raise ValidationError('Challenge rating must be more than 21.')
        if data_key == 'proficiency_bonus' and value:
            if value < 2 or value > 9:
                raise ValidationError('Proficiency bonus must be between 2 and 9.')
  

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
