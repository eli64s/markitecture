from typing import Tuple

from markitecture.metrics.analyzer import ReadabilityMetrics
from markitecture.metrics.badges.base import BaseSvgGenerator


class CompactBadgeGenerator(BaseSvgGenerator):
    def __init__(
        self,
        width: int = 400,
        height: int = 40,
        gradient: Tuple[str, str] = ("#7934C5", "#4158D0"),
    ):
        super().__init__(width, height)
        self.gradient = gradient

    def generate(self, metrics: ReadabilityMetrics) -> str:
        gradient_def = (
            f"<defs>\n"
            f"  <linearGradient id='gradientBg' x1='0%' y1='0%' x2='100%' y2='0%'>\n"
            f"    <stop offset='0%' style='stop-color:{self.gradient[0]}' />\n"
            f"    <stop offset='100%' style='stop-color:{self.gradient[1]}' />\n"
            f"  </linearGradient>\n"
            f"</defs>\n"
        )
        content = (
            f"<!-- Compact badge content -->\n"
            f"<rect x='0' y='0' width='{self.width}' height='{self.height}' rx='20' fill='white' "
            f"stroke='url(#gradientBg)' stroke-width='2' />\n"
            f"<text x='20' y='{self.height / 2}' font-family='Arial, sans-serif' font-size='14' fill='#666' "
            f"dominant-baseline='middle'>"
            f"{metrics.reading_time_mins}m read • {metrics.word_count:,} words • {metrics.complexity_score}% complexity"
            f"</text>\n"
        )
        return self.render(gradient_def + content)
