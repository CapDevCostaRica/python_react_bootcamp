"""
Domain entity representing a cache operation result.
Keeps track of cache operation metadata for metrics and observability.
"""
from dataclasses import dataclass
from typing import Any


@dataclass
class CacheResult:
    data: Any
    is_cached: bool
    source: str 