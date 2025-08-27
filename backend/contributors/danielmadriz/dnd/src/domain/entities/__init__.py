"""
Domain entities package.
Exports all domain entities for easy importing.
"""
from .monster import Monster
from .monster_list import MonsterList
from .cache_result import CacheResult

__all__ = [
    'Monster',
    'MonsterList', 
    'CacheResult'
] 