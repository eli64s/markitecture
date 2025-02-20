from typing import Dict

from markitecture.metrics.analyzer import ReadabilityMetrics


class ShieldsBadgeGenerator:
    def __init__(self):
        self.HEIGHT = 20
        self.FONT_SIZE = 11
        self.TEXT_MARGIN = 6
        self.COLORS = {
            "low": "#7934C5",  # Purple
            "medium": "#00E5FF",  # Cyan
            "high": "#FFD700",  # Gold
        }
        self.SHIELDS_BG = "#555555"

    def _calculate_width(self, text: str) -> int:
        return len(text) * 6 + self.TEXT_MARGIN * 2

    def _get_status_color(self, score: float) -> str:
        if score < 40:
            return self.COLORS["low"]
        elif score < 70:
            return self.COLORS["medium"]
        return self.COLORS["high"]

    def generate_reading_time_badge(self, minutes: float) -> str:
        label = "reading time"
        status = f"{minutes} min"
        label_width = self._calculate_width(label)
        status_width = self._calculate_width(status)
        total_width = label_width + status_width
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{self.HEIGHT}">
  <linearGradient id="smooth" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="round">
    <rect width="{total_width}" height="{self.HEIGHT}" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#round)">
    <rect width="{label_width}" height="{self.HEIGHT}" fill="{self.SHIELDS_BG}"/>
    <rect x="{label_width}" width="{status_width}" height="{self.HEIGHT}" fill="#4c1"/>
    <rect width="{total_width}" height="{self.HEIGHT}" fill="url(#smooth)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="{self.FONT_SIZE}">
    <text x="{label_width / 2}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_width / 2}" y="14">{label}</text>
    <text x="{label_width + status_width / 2}" y="15" fill="#010101" fill-opacity=".3">{status}</text>
    <text x="{label_width + status_width / 2}" y="14">{status}</text>
  </g>
</svg>'''

    def generate_complexity_badge(self, score: float) -> str:
        label = "complexity"
        status = f"{score}%"
        color = self._get_status_color(score)
        label_width = self._calculate_width(label)
        status_width = self._calculate_width(status)
        total_width = label_width + status_width
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{self.HEIGHT}">
  <linearGradient id="smooth" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="round">
    <rect width="{total_width}" height="{self.HEIGHT}" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#round)">
    <rect width="{label_width}" height="{self.HEIGHT}" fill="{self.SHIELDS_BG}"/>
    <rect x="{label_width}" width="{status_width}" height="{self.HEIGHT}" fill="{color}"/>
    <rect width="{total_width}" height="{self.HEIGHT}" fill="url(#smooth)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="{self.FONT_SIZE}">
    <text x="{label_width / 2}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_width / 2}" y="14">{label}</text>
    <text x="{label_width + status_width / 2}" y="15" fill="#010101" fill-opacity=".3">{status}</text>
    <text x="{label_width + status_width / 2}" y="14">{status}</text>
  </g>
</svg>'''

    def generate_stats_badge(self, count: int, label: str, color: str) -> str:
        status = str(count)
        label_width = self._calculate_width(label)
        status_width = self._calculate_width(status)
        total_width = label_width + status_width
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{self.HEIGHT}">
  <linearGradient id="smooth" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="round">
    <rect width="{total_width}" height="{self.HEIGHT}" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#round)">
    <rect width="{label_width}" height="{self.HEIGHT}" fill="{self.SHIELDS_BG}"/>
    <rect x="{label_width}" width="{status_width}" height="{self.HEIGHT}" fill="{color}"/>
    <rect width="{total_width}" height="{self.HEIGHT}" fill="url(#smooth)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="{self.FONT_SIZE}">
    <text x="{label_width / 2}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_width / 2}" y="14">{label}</text>
    <text x="{label_width + status_width / 2}" y="15" fill="#010101" fill-opacity=".3">{status}</text>
    <text x="{label_width + status_width / 2}" y="14">{status}</text>
  </g>
</svg>'''

    def generate_badges(self, metrics: ReadabilityMetrics) -> Dict[str, str]:
        return {
            "reading_time": self.generate_reading_time_badge(metrics.reading_time_mins),
            "complexity": self.generate_complexity_badge(metrics.complexity_score),
            "words": self.generate_stats_badge(metrics.word_count, "words", "#1E90FF"),
            "headings": self.generate_stats_badge(
                metrics.heading_count, "headings", "#9370DB"
            ),
            "code_blocks": self.generate_stats_badge(
                metrics.code_block_count, "code blocks", "#FF6347"
            ),
            "links": self.generate_stats_badge(metrics.link_count, "links", "#20B2AA"),
            "images": self.generate_stats_badge(
                metrics.image_count, "images", "#DEB887"
            ),
        }
