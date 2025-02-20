"""Pydantic functions and type annotations to validate user input."""

from pathlib import Path
from typing import Annotated

from pydantic import AfterValidator

from markitecture.errors import InvalidPathError


def convert_to_path(v: str) -> Path:
    """Convert the path string to a Path object."""
    return Path(v)


def validate_path(v: Path) -> Path:
    """Ensure the path exists and is a file."""
    if not v.exists() or not v.is_file():
        raise InvalidPathError(
            message="The provided path does not exist or is not a file.",
            path=str(v),
        )
    return v


ExistingFilePath = Annotated[Path, AfterValidator(validate_path)]
