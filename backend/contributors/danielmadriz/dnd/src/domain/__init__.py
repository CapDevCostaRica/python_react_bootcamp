"""
Domain Layer - Business entities and interfaces.
"""
from .entities import Monster, MonsterList, CacheResult
from .interfaces import (
    IMonsterRepository,
    IMonsterApiClient,
    IMonsterService
)

__all__ = [
    # Entities
    'Monster',
    'MonsterList',
    'CacheResult',
    # Interfaces
    'IMonsterRepository',
    'IMonsterApiClient', 
    'IMonsterService'
] 