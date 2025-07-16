"""Pydantic functions and type annotations to validate user input."""

from pathlib import Path
from typing import Annotated, List, Optional, Pattern

from pydantic import AfterValidator, BaseModel, Field

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


class ValidatorSettings(BaseModel):
    """Settings for the link validator."""
    timeout: int = Field(default=10, ge=1, description="Timeout for network requests in seconds.")
    max_workers: int = Field(default=5, ge=1, description="Maximum number of concurrent validation workers.")
    allow_external_validation: bool = Field(default=True, description="Whether to validate external HTTP(S) links.")
    ignore_patterns: Optional[List[Pattern[str]]] = Field(
        default_factory=list, description="List of regex patterns to ignore URLs."
    )
    # base_url could also be a part of settings if needed for resolving relative links universally
    # For now, assuming base_dir in validate_across_files_async serves this.

    class Config:
        arbitrary_types_allowed = True # To allow Pattern objects
