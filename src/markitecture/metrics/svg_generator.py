from typing import Callable, Dict, Tuple

from markitecture.metrics.analyzer import ReadabilityMetrics
from markitecture.metrics.badges import (
    BadgeStyle,
    CompactBadgeGenerator,
    DetailedBadgeGenerator,
    MinimalBadgeGenerator,
    ModernBadgeGenerator,
    RetroBadgeGenerator,
    ShieldsBadgeGenerator,
)


class MetricsSvgGenerator:
    def __init__(self):
        self.dimensions: Dict[BadgeStyle, Tuple[int, int]] = {
            BadgeStyle.MODERN: (560, 140),
            BadgeStyle.COMPACT: (400, 40),
            BadgeStyle.DETAILED: (600, 200),
            BadgeStyle.MINIMAL: (300, 80),
            BadgeStyle.RETRO: (480, 120),
        }
        self.generators: Dict[BadgeStyle, Callable[[ReadabilityMetrics], str]] = {
            BadgeStyle.MODERN: ModernBadgeGenerator().generate,
            BadgeStyle.COMPACT: CompactBadgeGenerator().generate,
            BadgeStyle.DETAILED: DetailedBadgeGenerator().generate,
            BadgeStyle.MINIMAL: MinimalBadgeGenerator().generate,
            BadgeStyle.RETRO: RetroBadgeGenerator().generate,
            BadgeStyle.SHIELDS: self._generate_shields_badge,
        }

    def _get_gradient_colors(self, score: float) -> Tuple[str, str]:
        if score < 40:
            return ("#7934C5", "#4158D0")
        elif score < 70:
            return ("#00E5FF", "#4158D0")
        return ("#FFD700", "#FF00FF")

    def _generate_shields_badge(
        self, metrics: ReadabilityMetrics, color_start: str, color_end: str
    ) -> str:
        generator = ShieldsBadgeGenerator()
        badges = generator.generate_badges(metrics)
        width = max(self.dimensions.get(BadgeStyle.MODERN, (560,))[0], 560)
        total_height = (len(badges) * 25) + 20
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {total_height}">
  <defs>
    <style>
      @font-face {{
        font-family: "DejaVu Sans";
        src: url("https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.3/ttf/DejaVuSans.ttf");
      }}
    </style>
  </defs>"""
        y_pos = 10
        for badge_svg in badges.values():
            content = badge_svg.split(">", 1)[1].rsplit("</svg>", 1)[0]
            svg += f'\n  <g transform="translate(10, {y_pos})">\n    {content}\n  </g>'
            y_pos += 25
        svg += "\n</svg>"
        return svg

    def generate_svg(self, metrics: ReadabilityMetrics, style: BadgeStyle) -> str:
        if style not in self.generators:
            raise ValueError(f"Style '{style}' not supported.")
        if style == BadgeStyle.SHIELDS:
            color_start, color_end = self._get_gradient_colors(metrics.complexity_score)
            return self.generators[style](metrics, color_start, color_end)
        return self.generators[style](metrics)
