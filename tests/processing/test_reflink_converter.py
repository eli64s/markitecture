from pathlib import Path

import pytest

from markitecture.processing.reflink_converter import (
    ReferenceLinkConverter,
    ReferencePlacement,
)

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
def converter():
    """Create a ReferenceLinkConverter instance."""
    return ReferenceLinkConverter()


def test_convert_to_reflinks_placement_end(converter: ReferenceLinkConverter):
    """Test conversion with reference placement at the end of the document."""
    converted_text = converter.convert_to_reflinks(
        sample_md_inline_links, placement=ReferencePlacement.END
    )

    # Assertions for links
    assert "[inline link to Google][inline-link-to-google]" in converted_text
    assert "[link to OpenAI][link-to-openai]" in converted_text
    assert (
        "[link to Pydantic's documentation][link-to-pydantics-documentation]"
        in converted_text
    )
    assert "![alt text for image][alt-text-for-image]" in converted_text

    # Assertions for reference definitions at the end
    expected_refs_end = """
[alt-text-for-image]: images/my_image.png
[inline-link-to-google]: https://www.google.com
[link-to-openai]: https://www.openai.com
[link-to-pydantics-documentation]: https://docs.pydantic.dev/
"""
    # Normalize whitespace for comparison
    assert "".join(expected_refs_end.split()) in "".join(converted_text.split())


def test_convert_to_reflinks_placement_section(converter: ReferenceLinkConverter):
    """Test conversion with reference placement at the end of each section."""
    converted_text = converter.convert_to_reflinks(
        sample_md_with_sections, placement=ReferencePlacement.SECTION
    )

    # Chapter 1 Assertions
    assert "Some text with [an inline link][an-inline-link]." in converted_text
    # Check for reference definition at the end of Section 1.1 (which is the section for the first link)
    # The logic places it at the end of the heading block it belongs to.
    section_1_1_expected_ref = """
[another-link]: https://example.com/page2
[an-inline-link]: https://example.com/page1
"""
    # Normalize whitespace for comparison
    assert "".join(section_1_1_expected_ref.split()) in "".join(converted_text.split())

    # Chapter 2 Assertions
    assert "Text for chapter 2, including a [third link][third-link]." in converted_text
    chapter_2_expected_ref = """
[third-link]: https://example.com/page3
"""
    assert "".join(chapter_2_expected_ref.split()) in "".join(converted_text.split())


def test_process_file_new_output(converter: ReferenceLinkConverter, tmp_path: Path):
    """Test processing a file and saving to a new output file."""
    input_file = tmp_path / "input.md"
    output_file = tmp_path / "output.md"
    input_file.write_text(sample_md_inline_links)

    converter.process_file(input_file, output_file, placement=ReferencePlacement.END)

    assert output_file.exists()
    converted_text = output_file.read_text()

    assert "[inline link to Google][inline-link-to-google]" in converted_text
    assert "![alt text for image][alt-text-for-image]" in converted_text
    expected_refs_end = """
[alt-text-for-image]: images/my_image.png
[inline-link-to-google]: https://www.google.com
[link-to-openai]: https://www.openai.com
[link-to-pydantics-documentation]: https://docs.pydantic.dev/
"""
    assert "".join(expected_refs_end.split()) in "".join(converted_text.split())


def test_process_file_inplace_modification(
    converter: ReferenceLinkConverter, tmp_path: Path
):
    """Test processing a file with in-place modification."""
    input_file = tmp_path / "input_inplace.md"
    input_file.write_text(sample_md_inline_links)

    converter.process_file(input_file, None, placement=ReferencePlacement.END)

    # File should have been modified
    converted_text = input_file.read_text()

    assert "[inline link to Google][inline-link-to-google]" in converted_text
    assert "![alt text for image][alt-text-for-image]" in converted_text
    expected_refs_end = """
[alt-text-for-image]: images/my_image.png
[inline-link-to-google]: https://www.google.com
[link-to-openai]: https://www.openai.com
[link-to-pydantics-documentation]: https://docs.pydantic.dev/
"""
    assert "".join(expected_refs_end.split()) in "".join(converted_text.split())
