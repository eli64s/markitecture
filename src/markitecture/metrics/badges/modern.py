# markitecture/metrics/badges/modern.py
from typing import Tuple

from markitecture.metrics.analyzer import ReadabilityMetrics
from markitecture.metrics.badges.base import BaseSvgGenerator


class ModernBadgeGenerator(BaseSvgGenerator):
    def __init__(
        self,
        width: int = 560,
        height: int = 140,
        gradient: Tuple[str, str] = ("#7934C5", "#4158D0"),
    ):
        super().__init__(width, height)
        self.gradient = gradient

    def generate(self, metrics: ReadabilityMetrics) -> str:
        # Improved gradient with additional stops for a smoother transition.
        gradient_def = (
            f"<defs>\n"
            f"  <linearGradient id='gradientBg' x1='0%' y1='0%' x2='100%' y2='0%'>\n"
            f"    <stop offset='0%' style='stop-color:{self.gradient[0]}; stop-opacity:1' />\n"
            f"    <stop offset='50%' style='stop-color:#6A2C70; stop-opacity:0.8' />\n"
            f"    <stop offset='100%' style='stop-color:{self.gradient[1]}; stop-opacity:1' />\n"
            f"  </linearGradient>\n"
            f"  <filter id='dropShadow' x='-10%' y='-10%' width='120%' height='120%'>\n"
            f"    <feGaussianBlur in='SourceAlpha' stdDeviation='3' />\n"
            f"    <feOffset dx='3' dy='3' result='offsetblur'/>\n"
            f"    <feMerge>\n"
            f"      <feMergeNode/>\n"
            f"      <feMergeNode in='SourceGraphic'/>\n"
            f"    </feMerge>\n"
            f"  </filter>\n"
            f"</defs>\n"
        )
        content = (
            f"<!-- Improved Modern badge content -->\n"
            f"<rect x='0' y='0' width='{self.width}' height='{self.height}' fill='url(#gradientBg)' filter='url(#dropShadow)' rx='15'/>\n"
            f"<text x='30' y='{self.height / 2 - 10}' font-family='Helvetica, Arial, sans-serif' font-size='24' fill='white' font-weight='bold'>"
            f"{metrics.reading_time_mins} min read</text>\n"
            f"<text x='30' y='{self.height / 2 + 20}' font-family='Helvetica, Arial, sans-serif' font-size='16' fill='white'>"
            f"{metrics.word_count:,} words | {metrics.complexity_score}% complexity</text>\n"
        )
        return self.render(gradient_def + content)
