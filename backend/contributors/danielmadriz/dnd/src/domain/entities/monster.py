"""
Domain entity representing a D&D monster.
"""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Monster:
    index: str
    name: str
    url: str
    data: Dict[str, Any] 