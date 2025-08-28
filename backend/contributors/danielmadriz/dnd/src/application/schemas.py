"""
Marshmallow schemas for input validation and output serialization.
"""
from marshmallow import Schema, fields, ValidationError, validates_schema, post_load
from typing import Dict, Any


class MonsterRequestSchema(Schema):
    """Schema for POST /get monster request validation."""
    monster_index = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    
    @validates_schema
    def validate_monster_index(self, data, **kwargs):
        """Custom validation for monster_index."""
        if not data.get('monster_index') or not data['monster_index'].strip():
            raise ValidationError('monster_index is required and cannot be empty')


class MonsterListRequestSchema(Schema):
    """Schema for POST /list monster request validation."""
    resource = fields.Str(required=True, validate=lambda x: x == 'monsters')
    
    @validates_schema
    def validate_resource(self, data, **kwargs):
        """Custom validation for resource field."""
        if data.get('resource') != 'monsters':
            raise ValidationError('resource must be "monsters"')


class MonsterResponseSchema(Schema):
    """Schema for monster response serialization."""
    index = fields.Str(required=True)
    name = fields.Str(required=True)
    url = fields.Str(required=True)
    data = fields.Dict(keys=fields.Str(), values=fields.Raw(), required=True)


class MonsterListResponseSchema(Schema):
    """Schema for monster list response serialization."""
    count = fields.Int(required=True)
    results = fields.List(fields.Nested(MonsterResponseSchema), required=True)


class CacheInfoSchema(Schema):
    """Schema for cache information in responses."""
    cached = fields.Bool(required=True)
    source = fields.Str(required=True)


class CachedResponseSchema(Schema):
    """Schema for responses with cache information."""
    data = fields.Raw(required=True)
    cache_info = fields.Nested(CacheInfoSchema, required=True)


class ErrorResponseSchema(Schema):
    """Schema for error responses."""
    error = fields.Str(required=True)
    message = fields.Str(required=True)
    status_code = fields.Int(required=True)


class HealthResponseSchema(Schema):
    """Schema for health check response."""
    status = fields.Str(required=True)
    service = fields.Str(required=True)
    version = fields.Str(required=True)
    endpoints = fields.Dict(keys=fields.Str(), values=fields.Str(), required=True)
