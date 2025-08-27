"""
Domain entity representing a list of monsters.
"""
from dataclasses import dataclass
from typing import List
from .monster import Monster


@dataclass
class MonsterList:
    monsters: List[Monster]
    count: int 