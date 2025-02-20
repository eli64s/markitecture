from markitecture.metrics.analyzer import ReadabilityMetrics
from markitecture.metrics.badges.base import BaseSvgGenerator


class RetroBadgeGenerator(BaseSvgGenerator):
    def __init__(self, width: int = 480, height: int = 120):
        super().__init__(width, height)

    def generate(self, metrics: ReadabilityMetrics) -> str:
        content = (
            f"<!-- Retro badge content -->\n"
            f"<rect x='4' y='4' width='{self.width - 8}' height='{self.height - 8}' fill='white' stroke='#333' stroke-width='2' />\n"
            f"<rect x='0' y='0' width='4' height='4' fill='#333' />\n"
            f"<rect x='{self.width - 4}' y='0' width='4' height='4' fill='#333' />\n"
            f"<rect x='0' y='{self.height - 4}' width='4' height='4' fill='#333' />\n"
            f"<rect x='{self.width - 4}' y='{self.height - 4}' width='4' height='4' fill='#333' />\n"
            f"<text x='{self.width / 2}' y='40' font-family='Courier, monospace' font-size='16' fill='#333' text-anchor='middle'>DOCUMENT METRICS</text>\n"
            f"<text x='{self.width / 2}' y='70' font-family='Courier, monospace' font-size='14' fill='#666' text-anchor='middle'>"
            f"{metrics.reading_time_mins}m | {metrics.word_count:,} words | {metrics.complexity_score}% comp.</text>\n"
            f"<text x='{self.width / 2}' y='95' font-family='Courier, monospace' font-size='12' fill='#999' text-anchor='middle'>"
            f"H:{metrics.heading_count} C:{metrics.code_block_count} L:{metrics.link_count} I:{metrics.image_count}</text>\n"
        )
        return self.render(content)
