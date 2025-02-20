from pathlib import Path

import pytest
import pytest_mock

from markitecture.cli.app import run_cli
from markitecture.errors import InvalidPathError
from markitecture.settings.config import MarkitectureApp
from markitecture.settings.validators import validate_path


def test_run_cli(capsys: pytest.CaptureFixture[str]):
    run_cli()
    captured = capsys.readouterr().out
    assert "No command provided" in captured


def test_markitecture_settings():
    settings = MarkitectureApp()
    assert isinstance(settings, MarkitectureApp)


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
