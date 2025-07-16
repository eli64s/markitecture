import subprocess
import sys
from pathlib import Path

import pytest

sample_md_inline_links = """
# My Document

This is a paragraph with an [inline link to Google](https://www.google.com).
Here is another [link to OpenAI](https://www.openai.com) in the same paragraph.

Another paragraph with a [link to Pydantic's documentation](https://docs.pydantic.dev/).
And an image: ![alt text for image](images/my_image.png)
"""

sample_md_with_sections = """
# Chapter 1

Some text with [an inline link](https://example.com/page1).

## Section 1.1

More text and [another link](https://example.com/page2) for this section.

# Chapter 2

Text for chapter 2, including a [third link](https://example.com/page3).
"""


@pytest.fixture
def create_temp_md_file(tmp_path: Path):
    """Fixture to create a temporary markdown file with given content."""

    def _create_file(filename: str, content: str) -> Path:
        file_path = tmp_path / filename
        file_path.write_text(content, encoding="utf-8")
        return file_path

    return _create_file


def run_markitect_cli(args: list[str]) -> subprocess.CompletedProcess:
    """Helper function to run the Markitecture CLI."""
    command = [sys.executable, "-m", "markitecture"] + args
    return subprocess.run(
        command, capture_output=True, text=True, check=False, cwd="/app"
    )


expected_refs_end_content_snippet = """
[alt-text-for-image]: images/my_image.png
[inline-link-to-google]: https://www.google.com
[link-to-openai]: https://www.openai.com
[link-to-pydantics-documentation]: https://docs.pydantic.dev/
"""


def normalize_whitespace(text: str) -> str:
    """Normalizes whitespace in a string for comparison."""
    return "".join(text.split())


def test_cli_reflinks_to_new_file_placement_end(create_temp_md_file, tmp_path: Path):
    """Test CLI reflinks to a new file with 'end' placement."""
    input_filename = "input.md"
    input_md_path = create_temp_md_file(input_filename, sample_md_inline_links)

    result = run_markitect_cli(
        [
            "links",
            "reflinks",
            str(input_md_path),
        ]
    )

    assert result.returncode == 0, f"CLI Error: {result.stderr or result.stdout}"

    modified_content = input_md_path.read_text(encoding="utf-8")

    # Check for converted links
    assert "[inline link to Google][inline-link-to-google]" in modified_content
    assert "![alt text for image][alt-text-for-image]" in modified_content
    # Check for reference definitions
    assert normalize_whitespace(
        expected_refs_end_content_snippet
    ) in normalize_whitespace(modified_content)


def test_cli_reflinks_help():
    """Test that the 'links reflinks --help' command works."""
    result = run_markitect_cli(["links", "reflinks", "--help"])
    assert result.returncode == 0
    assert "usage: markitecture links reflinks" in result.stdout


def test_cli_links_help():
    """Test that the 'links --help' command works and shows subcommands."""
    result = run_markitect_cli(["links", "--help"])
    assert result.returncode == 0
    assert "usage: markitecture links" in result.stdout
    assert "{check,reflinks}" in result.stdout
