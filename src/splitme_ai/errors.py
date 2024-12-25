"""Custom exceptions for the splitme-ai package."""

from __future__ import annotations


class SplitmeAIBaseError(Exception):
    """Base exception for splitme-ai errors."""

    ...


class ParseError(SplitmeAIBaseError):
    """Raised when parsing markdown content fails."""

    ...


class FileOperationError(SplitmeAIBaseError):
    """Raised when file operations fail."""

    ...


# -- CLI Exceptions -----------------------------------------------------------


class CLIError(SplitmeAIBaseError):
    """Exceptions related to the CLI."""

    def __init__(self, message, *args):
        super().__init__(f"Invalid option provided to CLI: {message}", *args)


# -- File IO Exceptions -------------------------------------------------------


class FileSystemError(SplitmeAIBaseError):
    """Exceptions related to file system operations."""

    def __init__(self, message, path, *args):
        self.file_path = path
        super().__init__(f"{message}: {path}", *args)


class FileReadError(FileSystemError):
    """Could not read file."""

    ...


class FileWriteError(FileSystemError):
    """Could not write file."""

    ...


# -- <ERROR TYPE> ---------------------------------------------
