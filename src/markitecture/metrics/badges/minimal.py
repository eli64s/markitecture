from markitecture.metrics.analyzer import ReadabilityMetrics
from markitecture.metrics.badges.base import BaseSvgGenerator


class MinimalBadgeGenerator(BaseSvgGenerator):
    def __init__(self, width: int = 300, height: int = 80, color: str = "#7934C5"):
        super().__init__(width, height)
        self.color = color

    def generate(self, metrics: ReadabilityMetrics) -> str:
        content = (
            f"<!-- Minimal badge content -->\n"
            f"<rect x='0' y='0' width='{self.width}' height='{self.height}' fill='white' />\n"
            f"<text x='20' y='30' font-family='Arial, sans-serif' font-size='16' fill='#333'>"
            f"{metrics.reading_time_mins} min read</text>\n"
            f"<text x='20' y='55' font-family='Arial, sans-serif' font-size='14' fill='{self.color}'>"
            f"{metrics.complexity_score}% complexity</text>\n"
        )
        return self.render(content)
