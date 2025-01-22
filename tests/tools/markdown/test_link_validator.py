import pytest

from splitme.tools.markdown.link_validator import LinkValidator


@pytest.fixture
def validator() -> LinkValidator:
    return LinkValidator()


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
    links = validator.extract_links(content)
    assert links == expected
