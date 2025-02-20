"""Custom exceptions for the markitecture package."""

from __future__ import annotations

from typing import Any

# -------------------------------------------------------------------
# Base Exceptions
# -------------------------------------------------------------------


class MarkitectureBaseError(Exception):
    """Base exception for markitecture errors."""

    ...


class ParseError(MarkitectureBaseError):
    """Raised when parsing markdown content fails."""

    ...


class FileOperationError(MarkitectureBaseError):
    """Raised when file operations fail."""

    ...


# -------------------------------------------------------------------
# Command-Line Interface (CLI) Exceptions
# -------------------------------------------------------------------


class CLIError(MarkitectureBaseError):
    """Exceptions related to the CLI."""

    def __init__(self, message: str, *args: Any) -> None:
        super().__init__(f"Invalid option provided to CLI: {message}", *args)


# -------------------------------------------------------------------
# File System Exceptions
# -------------------------------------------------------------------


class FileSystemError(MarkitectureBaseError):
    """Exceptions related to file system operations."""

    def __init__(self, message: str, path: str, *args: Any) -> None:
        self.file_path = path
        super().__init__(f"{message}: {path}", *args)


class FileReadError(FileSystemError):
    """Could not read file."""

    ...


class FileWriteError(FileSystemError):
    """Could not write file."""

    ...


class InvalidPathError(FileSystemError):
    """Invalid path provided."""

    ...
