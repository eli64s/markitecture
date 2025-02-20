import pytest

from markitecture.metrics.analyzer import ReadabilityAnalyzer, ReadabilityMetrics

SAMPLE_TEXTS = [
    (
        "This is a simple sentence. And another one!",
        {
            "word_count": 9,
            "sentence_count": 2,
            "code_block_count": 0,
            "heading_count": 0,
            "link_count": 0,
            "image_count": 0,
        },
    ),
    (
        "# Heading\nThis document contains a heading, a link: [example](http://example.com) "
        "and an image: ![alt](http://image.com/img.png).",
        {
            "word_count": 17,
            "sentence_count": 1,
            "heading_count": 1,
            "link_count": 1,
            "image_count": 1,
            "code_block_count": 0,
        },
    ),
    (
        "Here is some text.\n\n```python\nprint('Hello, World!')\n```\nMore text here.",
        {
            "word_count": 7,
            "sentence_count": 2,
            "code_block_count": 1,
            "heading_count": 0,
            "link_count": 0,
            "image_count": 0,
        },
    ),
]


@pytest.fixture
def analyzer() -> ReadabilityAnalyzer:
    """Provides a fresh ReadabilityAnalyzer for each test."""
    return ReadabilityAnalyzer()


@pytest.mark.parametrize("text, expected", SAMPLE_TEXTS)
def test_analyzer_counts(
    analyzer: ReadabilityAnalyzer, text: str, expected: dict
) -> None:
    """
    Test internal count functions using sample texts.
    Note: We use analyze_document as a proxy to verify counts.
    """
    metrics: ReadabilityMetrics = analyzer.analyze_document(text)

    # if "word_count" in expected:
    #     assert metrics.word_count == expected["word_count"], (
    #         f"Expected word count {expected['word_count']}, got {metrics.word_count}"
    #     )
    # if "sentence_count" in expected:
    #     assert metrics.sentence_count == expected["sentence_count"], (
    #         f"Expected sentence count {expected['sentence_count']}, got {metrics.sentence_count}"
    #     )
    if "code_block_count" in expected:
        assert metrics.code_block_count == expected["code_block_count"], (
            f"Expected code block count {expected['code_block_count']}, got {metrics.code_block_count}"
        )
    if "heading_count" in expected:
        assert metrics.heading_count == expected["heading_count"], (
            f"Expected heading count {expected['heading_count']}, got {metrics.heading_count}"
        )
    if "link_count" in expected:
        assert metrics.link_count == expected["link_count"], (
            f"Expected link count {expected['link_count']}, got {metrics.link_count}"
        )
    if "image_count" in expected:
        assert metrics.image_count == expected["image_count"], (
            f"Expected image count {expected['image_count']}, got {metrics.image_count}"
        )


def test_reading_time_calculation(analyzer: ReadabilityAnalyzer) -> None:
    """
    Verify that the reading time calculation includes code block penalty.
    """
    # 100 sentences, simple text
    text = "This is a sentence." * 100
    # Inject one code block at the end
    text += "\n```python\nprint('Extra code block')\n```"
    metrics = analyzer.analyze_document(text)
    # Calculate base reading time (ignoring code block)
    base_time = metrics.word_count / analyzer.READING_SPEED
    # Additional time for one code block (20 sec => 20/60 min)
    expected_time = round(base_time + (analyzer.CODE_BLOCK_TIME / 60), 1)
    assert metrics.reading_time_mins == expected_time, (
        f"Expected reading time {expected_time} minutes, got {metrics.reading_time_mins} minutes"
    )


def test_complexity_score_range(analyzer: ReadabilityAnalyzer) -> None:
    """
    Ensure that the complexity score is between 0 and 100.
    """
    text = "This is a simple text. " * 20
    metrics = analyzer.analyze_document(text)
    assert 0 <= metrics.complexity_score <= 100, (
        f"Complexity score out of bounds: {metrics.complexity_score}"
    )


def test_empty_document(analyzer: ReadabilityAnalyzer) -> None:
    """
    Test analyzer with an empty document.
    """
    metrics = analyzer.analyze_document("")
    assert metrics.word_count == 0
    assert metrics.sentence_count == 0
    assert metrics.reading_time_mins == 0
    # Complexity score should be 0 when there is no text.
    assert metrics.complexity_score == 0
