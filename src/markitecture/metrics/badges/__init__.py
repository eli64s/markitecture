from enum import StrEnum

from markitecture.metrics.badges.compact import CompactBadgeGenerator
from markitecture.metrics.badges.detailed import DetailedBadgeGenerator
from markitecture.metrics.badges.minimal import MinimalBadgeGenerator
from markitecture.metrics.badges.modern import ModernBadgeGenerator
from markitecture.metrics.badges.retro import RetroBadgeGenerator
from markitecture.metrics.badges.shields import ShieldsBadgeGenerator


class BadgeStyle(StrEnum):
    MODERN = "modern"
    COMPACT = "compact"
    DETAILED = "detailed"
    MINIMAL = "minimal"
    RETRO = "retro"
    SHIELDS = "shields"


__all__ = [
    "BadgeStyle",
    "CompactBadgeGenerator",
    "DetailedBadgeGenerator",
    "MinimalBadgeGenerator",
    "ModernBadgeGenerator",
    "RetroBadgeGenerator",
    "ShieldsBadgeGenerator",
]
