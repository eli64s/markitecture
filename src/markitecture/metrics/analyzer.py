import re
from dataclasses import dataclass
from typing import Tuple


@dataclass
class ReadabilityMetrics:
    """
    Data class to store readability metrics.
    """

    word_count: int
    sentence_count: int
    avg_words_per_sentence: float
    reading_time_mins: float
    complexity_score: float
    heading_count: int
    code_block_count: int
    link_count: int
    image_count: int


class ReadabilityAnalyzer:
    """
    Analyze the content and calculate readability metrics.
    """

    def __init__(self) -> None:
        self.READING_SPEED = 238  # words per minute
        self.CODE_BLOCK_TIME = 20  # seconds
        self.WEIGHTS = {
            "avg_sentence_length": 0.3,
            "code_density": 0.3,
            "heading_depth": 0.2,
            "link_density": 0.1,
            "image_density": 0.1,
        }

    def _count_words(self, text: str) -> int:
        """Count words in the text after removing code blocks and URLs."""
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"`.*?`", "", text)
        text = re.sub(r"http[s]?://\S+", "", text)
        words = re.findall(r"\w+", text)
        return len(words)

    def _count_sentences(self, text: str) -> int:
        """Split text into sentences and count them."""
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        sentences = re.split(r"[.!?]+", text)
        return len([s for s in sentences if s.strip()])

    def _count_code_blocks(self, text: str) -> int:
        """Count code blocks enclosed in triple backticks."""
        return len(re.findall(r"```.*?```", text, re.DOTALL))

    def _count_headings(self, text: str) -> Tuple[int, float]:
        """Calculate average heading depth."""
        headings = re.findall(r"^(#{1,6})\s+.*$", text, re.MULTILINE)
        if not headings:
            return 0, 0.0
        total_depth = sum(len(h) for h in headings)
        return len(headings), total_depth / len(headings)

    def _count_links_and_images(self, text: str) -> Tuple[int, int]:
        """Count links only if not preceded by an exclamation mark."""
        links = len(re.findall(r"(?<!\!)\[(.*?)\]\((.*?)\)", text))
        images = len(re.findall(r"!\[(.*?)\]\((.*?)\)", text))
        return links, images

    def calculate_complexity(self, metrics: ReadabilityMetrics) -> float:
        """Calculate a weighted complexity score based on various metrics."""
        scores = {
            "avg_sentence_length": min(metrics.avg_words_per_sentence / 20.0, 1.0),
            "code_density": metrics.code_block_count / max(metrics.word_count / 500, 1),
            "heading_depth": metrics.heading_count / max(metrics.word_count / 200, 1),
            "link_density": metrics.link_count / max(metrics.word_count / 200, 1),
            "image_density": metrics.image_count / max(metrics.word_count / 300, 1),
        }
        weighted_score = sum(
            scores[metric] * weight for metric, weight in self.WEIGHTS.items()
        )
        return min(round(weighted_score * 100), 100)

    def analyze_document(self, content: str) -> ReadabilityMetrics:
        """Analyze the content and calculate readability metrics."""
        word_count = self._count_words(content)
        sentence_count = self._count_sentences(content)
        code_blocks = self._count_code_blocks(content)
        heading_count, _ = self._count_headings(content)
        link_count, image_count = self._count_links_and_images(content)
        avg_words = word_count / max(sentence_count, 1) if sentence_count > 0 else 0
        base_reading_time = word_count / self.READING_SPEED
        code_reading_time = (code_blocks * self.CODE_BLOCK_TIME) / 60
        total_reading_time = base_reading_time + code_reading_time

        metrics = ReadabilityMetrics(
            word_count=word_count,
            sentence_count=sentence_count,
            avg_words_per_sentence=round(avg_words, 1),
            reading_time_mins=round(total_reading_time, 1),
            complexity_score=0,  # placeholder
            heading_count=heading_count,
            code_block_count=code_blocks,
            link_count=link_count,
            image_count=image_count,
        )
        metrics.complexity_score = self.calculate_complexity(metrics)
        return metrics
