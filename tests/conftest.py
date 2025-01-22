from pathlib import Path

import pytest

from splitme.utils.file_handler import FileHandler


@pytest.fixture
def file_handler() -> FileHandler:
    return FileHandler()


@pytest.fixture
def input_file(filename: str = "tests/data/markdown/readme-ai.md") -> str:
    """Return markdown file content."""
    file_path = Path.cwd() / filename
    return file_handler().read(file_path)
