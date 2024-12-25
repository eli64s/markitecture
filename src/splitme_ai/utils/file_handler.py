"""File handling utilities with error handling."""

from pathlib import Path
from typing import Union

from splitme_ai.errors import FileOperationError


class FileHandler:
    """Handles file operations with proper error handling."""

    def write(self, file_path: Union[str, Path], content: str) -> None:
        """Write content to file with error handling."""
        try:
            Path(file_path).write_text(content, encoding="utf-8")
        except Exception as e:
            raise FileOperationError(f"Failed to write to {file_path}: {e}") from e

    def read(self, file_path: Union[str, Path]) -> str:
        """Read content from file with error handling."""
        try:
            return Path(file_path).read_text(encoding="utf-8")
        except Exception as e:
            raise FileOperationError(f"Failed to read {file_path}: {e}") from e
