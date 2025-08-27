"""
Crosscutting Concerns - Shared utilities and exceptions.

"""
from .exceptions import (
    BaseError,
    ValidationError,
    ServiceError,
    NotFoundError,
    ExternalApiError,
    CacheError
)

__all__ = [
    'BaseError',
    'ValidationError',
    'ServiceError',
    'NotFoundError',
    'ExternalApiError',
    'CacheError'
] 