from pathlib import Path
from typing import Literal

import pytest

from markitecture.processing.link_validator import LinkValidator


@pytest.fixture
def sample_md_file(tmp_path: Path):
    """Creates a sample markdown file for testing."""
    file_path = tmp_path / "sample.md"
    file_path.write_text(
        """
        [Example Link](http://example.com)
        [Internal Link](#internal-anchor)
        [Broken Link](nonexistent-page)

        ## Internal Anchor
        """
    )
    return str(file_path)  # Return the path as a string


@pytest.mark.parametrize(
    "content, expected",
    [
        ("[example](http://example.com)", [("example", "http://example.com", 1)]),
        (
            "[example](http://example.com)\n[example2](http://example2.com)",
            [
                ("example", "http://example.com", 1),
                ("example2", "http://example2.com", 2),
            ],
        ),
        (
            "[example](http://example.com)\n[example2](http://example2.com)\n[example3](http://example3.com)",
            [
                ("example", "http://example.com", 1),
                ("example2", "http://example2.com", 2),
                ("example3", "http://example3.com", 3),
            ],
        ),
    ],
)
def test_extract_links(
    validator: LinkValidator, content: str, expected: list[tuple[str, str, int]]
):
    """
    Ensure extract_links finds all markdown links.
    """
    links = validator.extract_links(content)
    assert links == expected


@pytest.mark.parametrize(
    "url, expected_status",
    [
        ("http://example.com", "ok"),
        ("#local-anchor", "internal"),
        ("nonexistent-file.txt", "error"),
    ],
)
def test_check_link(
    validator: LinkValidator,
    url: Literal["http://example.com"]
    | Literal["#local-anchor"]
    | Literal["nonexistent-file.txt"],
    expected_status: Literal["ok"] | Literal["internal"] | Literal["error"],
):
    """
    Check if link validation yields correct status for different URL formats.
    """
    result = validator.check_link(url)
    assert result["status"] == expected_status


def test_link_validator_on_real_file(validator: LinkValidator, sample_md_file: str):
    """
    High-level integration test on an actual markdown file.
    """
    results = validator.check_markdown_file(sample_md_file)
    # we can assert no error or evaluate how many broken links found, etc.
    assert isinstance(results, list)
