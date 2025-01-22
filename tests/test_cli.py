from pathlib import Path

import pytest
import pytest_mock

from splitme.cli import SplitmeApp
from splitme.errors import InvalidPathError
from splitme.validators import validate_path


def test_splitme_settings():
    settings = SplitmeApp()
    assert isinstance(settings, SplitmeApp)


def test_validate_path_file_exists(mocker: pytest_mock.MockFixture):
    mock_path = mocker.Mock(spec=Path)
    mock_path.exists.return_value = True
    mock_path.is_file.return_value = True
    result = validate_path(mock_path)
    assert result == mock_path


def test_validate_path_file_does_not_exist(mocker: pytest_mock.MockFixture):
    mock_path = mocker.Mock(spec=Path)
    mock_path.exists.return_value = False
    with pytest.raises(InvalidPathError) as e:
        validate_path(mock_path)
    assert isinstance(e.value, InvalidPathError)


def test_validate_path_not_a_file(mocker: pytest_mock.MockFixture):
    mock_path = mocker.Mock(spec=Path)
    mock_path.exists.return_value = True
    mock_path.is_file.return_value = False
    with pytest.raises(InvalidPathError) as e:
        validate_path(mock_path)
    assert isinstance(e.value, InvalidPathError)
