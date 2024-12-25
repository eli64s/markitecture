from pathlib import Path

import pytest

from splitme_ai.utils.file_handler import FileHandler


def file_handler() -> FileHandler:
    """Return a file handler instance."""
    return FileHandler()


@pytest.fixture
def markdown_file(filename: str = "readme-ai.md") -> str:
    """Return markdown file content."""
    file_path = Path.cwd() / f"tests/data/{filename}"
    return file_handler().read(file_path)
