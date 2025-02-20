"""Test suite for ReferenceLinkConverter class."""

from pathlib import Path

import pytest

from markitecture.processing.reflink_converter import ReferenceLinkConverter


@pytest.fixture
def converter():
    """Create a ReferenceLinkConverter instance."""
    return ReferenceLinkConverter()


@pytest.fixture
def sample_content():
    """Sample markdown content with various link types."""
    return """# Test Document
This is a [simple link](https://example.com) in text.
Here's an [another link](https://example.org/page) to test.

## Images
And an ![image](https://example.com/image.png) too.
"""


@pytest.fixture
def temp_markdown_file(tmp_path: Path):
    """Create a temporary markdown file."""
    md_file = tmp_path / "test.md"
    content = """# Test
[Link 1](https://example.com)
![Image](https://example.com/image.jpg)"""
    md_file.write_text(content)
    return md_file
