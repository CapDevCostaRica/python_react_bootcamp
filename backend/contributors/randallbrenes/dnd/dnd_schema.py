# schemas.py
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models import RandallBrenesDnD

class DnDSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RandallBrenesDnD
        load_instance = True
        include_fk = True
        include_relationships = True
        sqla_session = None

    armor_class = auto_field()
    speed = auto_field()
    proficiencies = auto_field()
    damage_vulnerabilities = auto_field()
    damage_resistances = auto_field()
    damage_immunities = auto_field()
    condition_immunities = auto_field()
    senses = auto_field()
    special_abilities = auto_field()
    actions = auto_field()
    legendary_actions = auto_field()
    forms = auto_field()
    reactions = auto_field()

class DnDMinSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RandallBrenesDnD
        fields = ("index", "name", "url")
        load_instance = True