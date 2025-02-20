from pathlib import Path

import pytest

from markitecture.utils.sanitizer import sanitize_filename


@pytest.mark.parametrize(
    ("filename", "expected_path"),
    [
        ("", Path("unnamed-section.md")),
        ("#### Header", Path("header.md")),
        ("Header {#custom-id}", Path("header.md")),
        ("Header {#}", Path("header.md")),
        ("![ ][ref]", Path("unnamed-section.md")),
        ("![alt text][ref] Header", Path("alt-text-header.md")),
        ("Header with spaces and CAPS", Path("header-with-spaces-and-caps.md")),
        (
            "Header *with* special _characters_",
            Path("header-with-special-characters.md"),
        ),
        (
            """#### <img width="2%" src="https://simpleicons.org/icons/docker.svg">&emsp13;Docker""",
            Path("docker.md"),
        ),
        # ("Header &amp; More", Path("header-and-more.md")),
        # ("Header & More", Path("header-and-more.md")),
    ],
)
def test_sanitize_filename(filename: str, expected_path: Path):
    assert sanitize_filename(filename) == expected_path


def test_sanitize_filename_custom_extension():
    assert sanitize_filename("Header", extension=".txt") == Path("header.txt")
