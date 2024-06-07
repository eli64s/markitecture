import pytest

from kenshi.splitters.markdown import MarkdownHeaderTextSplitter


@pytest.fixture
def text_splitter():
    headers_to_split_on = [("#", "h1"), ("##", "h2"), ("###", "h3")]
    return MarkdownHeaderTextSplitter(headers_to_split_on)


def test_empty_input(text_splitter):
    text = ""
    chunks = text_splitter.split_text(text)
    assert len(chunks) == 0


def test_no_headers(text_splitter):
    text = "This is a text without headers."
    chunks = text_splitter.split_text(text)
    assert len(chunks) == 1
    assert chunks[0]["page_content"] == "This is a text without headers."
    assert chunks[0]["metadata"] == {}


def test_leading_trailing_whitespace(text_splitter):
    text = "  \n  # Header\n\nContent\n  \n"
    chunks = text_splitter.split_text(text)
    assert len(chunks) == 1
    assert chunks[0]["page_content"] == "  \n  # Header\n\nContent\n  \n"
    assert chunks[0]["metadata"] == {"h1": "Header"}


def test_consecutive_headers(text_splitter):
    text = "## Header1 ## Header2\n\nContent"
    chunks = text_splitter.split_text(text)
    assert len(chunks) == 2
    assert chunks[0]["page_content"] == "## Header1"
    assert chunks[0]["metadata"] == {"h2": "Header1"}
    assert chunks[1]["page_content"] == "## Header2\n\nContent"
    assert chunks[1]["metadata"] == {"h2": "Header2"}


def test_nested_headers(text_splitter):
    text = "# Header1\n\n## Header2\n\n### Header3\n\nContent"
    chunks = text_splitter.split_text(text)
    assert len(chunks) == 3
    assert chunks[0]["page_content"] == "# Header1"
    assert chunks[0]["metadata"] == {"h1": "Header1"}
    assert chunks[1]["page_content"] == "## Header2"
    assert chunks[1]["metadata"] == {"h1": "Header1", "h2": "Header2"}
    assert chunks[2]["page_content"] == "### Header3\n\nContent"
    assert chunks[2]["metadata"] == {"h1": "Header1", "h2": "Header2", "h3": "Header3"}


def test_code_blocks(text_splitter):
    text = "```\n# Header\nContent\n```\n\n# Real Header\n\nText"
    chunks = text_splitter.split_text(text)
    assert len(chunks) == 2
    assert chunks[0]["page_content"] == "```\n# Header\nContent\n```"
    assert chunks[0]["metadata"] == {}
    assert chunks[1]["page_content"] == "# Real Header\n\nText"
    assert chunks[1]["metadata"] == {"h1": "Real Header"}


def test_non_printable_characters(text_splitter):
    text = "# Header\n\nContent with\nnon-printable\x07characters"
    chunks = text_splitter.split_text(text)
    assert len(chunks) == 1
    assert (
        chunks[0]["page_content"] == "# Header\n\nContent with\nnon-printablecharacters"
    )
    assert chunks[0]["metadata"] == {"h1": "Header"}


def test_custom_headers(text_splitter):
    headers_to_split_on = [("==", "Section")]
    custom_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
    text = "==Section1==\n\nContent\n\n==Section2==\n\nMore content"
    chunks = custom_splitter.split_text(text)
    assert len(chunks) == 2
    assert chunks[0]["page_content"] == "==Section1==\n\nContent"
    assert chunks[0]["metadata"] == {"Section": "Section1"}
    assert chunks[1]["page_content"] == "==Section2==\n\nMore content"
    assert chunks[1]["metadata"] == {"Section": "Section2"}


def test_strip_headers(text_splitter):
    text_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
        strip_headers=False,
    )
    text = "# Header1\n\nContent\n\n## Header2\n\nMore content"
    chunks = text_splitter.split_text(text)
    assert len(chunks) == 2
    assert chunks[0]["page_content"] == "# Header1\n\nContent"
    assert chunks[0]["metadata"] == {"h1": "Header1"}
    assert chunks[1]["page_content"] == "## Header2\n\nMore content"
    assert chunks[1]["metadata"] == {"h1": "Header1", "h2": "Header2"}


def test_return_each_line(text_splitter):
    text_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
        return_each_line=True,
    )
    text = "# Header1\n\nLine1\nLine2\n\n## Header2\n\nLine3"
    chunks = text_splitter.split_text(text)
    assert len(chunks) == 5
    assert chunks[0]["page_content"] == "# Header1"
    assert chunks[0]["metadata"] == {"h1": "Header1"}
    assert chunks[1]["page_content"] == "Line1"
    assert chunks[1]["metadata"] == {"h1": "Header1"}
    assert chunks[2]["page_content"] == "Line2"
    assert chunks[2]["metadata"] == {"h1": "Header1"}
    assert chunks[3]["page_content"] == "## Header2"
    assert chunks[3]["metadata"] == {"h1": "Header1", "h2": "Header2"}
    assert chunks[4]["page_content"] == "Line3"
    assert chunks[4]["metadata"] == {"h1": "Header1", "h2": "Header2"}
