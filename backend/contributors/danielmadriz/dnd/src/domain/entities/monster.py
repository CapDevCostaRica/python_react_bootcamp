"""
Domain entity representing a D&D monster.
"""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Monster:
    """Domain entity representing a D&D monster."""
    index: str
    name: str
    url: str
    data: Dict[str, Any]  # All monster properties from D&D 5e API 