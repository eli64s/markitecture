from pathlib import Path
from unittest import mock

import pytest

from markitecture.errors import InvalidPathError
from markitecture.settings.validators import validate_path


@pytest.mark.parametrize(
    "path, exists, is_file, should_raise",
    [
        (Path("tests/data/nonexistent/path"), False, False, True),
        (Path("tests/data/markdown"), True, False, True),
        (Path("tests/data/markdown/readme-ai.md"), True, True, False),
    ],
)
def test_validate_path(path: Path, exists: bool, is_file: bool, should_raise: bool):
    with (
        mock.patch.object(Path, "exists", return_value=exists),
        mock.patch.object(Path, "is_file", return_value=is_file),
    ):
        if should_raise:
            with pytest.raises(InvalidPathError):
                validate_path(path)
        else:
            assert validate_path(path) == path
