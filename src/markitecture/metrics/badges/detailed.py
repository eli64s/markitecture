from typing import Tuple

from markitecture.metrics.analyzer import ReadabilityMetrics
from markitecture.metrics.badges.base import BaseSvgGenerator


class DetailedBadgeGenerator(BaseSvgGenerator):
    def __init__(
        self,
        width: int = 600,
        height: int = 200,
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
            f"  <filter id='shadow' x='-20%' y='-20%' width='140%' height='140%'>\n"
            f"    <feGaussianBlur in='SourceAlpha' stdDeviation='2' />\n"
            f"    <feOffset dx='2' dy='2' />\n"
            f"    <feComponentTransfer>\n"
            f"      <feFuncA type='linear' slope='0.2' />\n"
            f"    </feComponentTransfer>\n"
            f"    <feMerge>\n"
            f"      <feMergeNode />\n"
            f"      <feMergeNode in='SourceGraphic' />\n"
            f"    </feMerge>\n"
            f"  </filter>\n"
            f"</defs>\n"
        )
        content = (
            f"<!-- Detailed badge content -->\n"
            f"<rect x='0' y='0' width='{self.width}' height='{self.height}' rx='15' fill='white' "
            f"stroke='url(#gradientBg)' stroke-width='2' filter='url(#shadow)' />\n"
            f"<text x='30' y='40' font-family='Arial, sans-serif' font-size='20' font-weight='bold' "
            f"fill='url(#gradientBg)'>Document Analytics</text>\n"
            f"<text x='30' y='80' font-family='Arial, sans-serif' font-size='14' fill='#666'>"
            f"Reading Time: {metrics.reading_time_mins} minutes</text>\n"
            f"<text x='30' y='105' font-family='Arial, sans-serif' font-size='14' fill='#666'>"
            f"Word Count: {metrics.word_count:,}</text>\n"
            f"<text x='30' y='130' font-family='Arial, sans-serif' font-size='14' fill='#666'>"
            f"Avg Words/Sentence: {metrics.avg_words_per_sentence:.1f}</text>\n"
            f"<text x='{self.width / 2 + 30}' y='80' font-family='Arial, sans-serif' font-size='14' fill='#666'>"
            f"Headings: {metrics.heading_count}</text>\n"
            f"<text x='{self.width / 2 + 30}' y='105' font-family='Arial, sans-serif' font-size='14' fill='#666'>"
            f"Code Blocks: {metrics.code_block_count}</text>\n"
            f"<text x='{self.width / 2 + 30}' y='130' font-family='Arial, sans-serif' font-size='14' fill='#666'>"
            f"Links: {metrics.link_count}</text>\n"
            f"<rect x='30' y='160' width='540' height='8' rx='4' fill='#eee' />\n"
            f"<rect x='30' y='160' width='{5.4 * metrics.complexity_score}' height='8' rx='4' fill='url(#gradientBg)' />\n"
            f"<text x='{self.width - 40}' y='170' font-family='Arial, sans-serif' font-size='12' fill='#666' text-anchor='end'>"
            f"{metrics.complexity_score}% Complexity</text>\n"
        )
        return self.render(gradient_def + content)
