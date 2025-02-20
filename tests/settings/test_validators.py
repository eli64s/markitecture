from pathlib import Path

import pytest

from markitecture.settings.validators import validate_path


@pytest.fixture
def mock_path(tmp_path: Path):
    return tmp_path / "test.txt"


def test_validate_path_file_exists(mock_path: Path):
    mock_path.write_text("test")
    result = validate_path(mock_path)
    assert result == mock_path
