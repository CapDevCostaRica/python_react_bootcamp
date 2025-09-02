from marshmallow import Schema, fields

class PeopleFindFiltersSchema(Schema):
    eye_color   = fields.String(load_default=None)
    hair_color  = fields.String(load_default=None)
    age         = fields.String(load_default=None)
    height_cm   = fields.String(load_default=None)
    weight_kg   = fields.String(load_default=None)
    nationality = fields.String(load_default=None)
    degree      = fields.String(load_default=None)
    institution = fields.String(load_default=None)
    family      = fields.String(load_default=None)
    food        = fields.String(load_default=None)
    hobby       = fields.String(load_default=None)
