from importlib.metadata import version

from splitme.config import Config as Config
from splitme.core import MarkdownSplitter
from splitme.errors import (
    FileOperationError,
    FileReadError,
    FileWriteError,
    InvalidPathError,
    ParseError,
    SplitmeBaseError,
)
from splitme.tools.markdown import link_validator, reflink_converter, reflink_extractor
from splitme.utils.file_handler import FileHandler

from .cli import main as cli_main

__version__ = version("splitme")
__all__: list[str] = [
    "Config",
    "FileHandler",
    "FileOperationError",
    "FileReadError",
    "FileWriteError",
    "InvalidPathError",
    "MarkdownSplitter",
    "ParseError",
    "SplitmeBaseError",
    "__version__",
    "cli_main",
    "link_validator",
    "reflink_converter",
    "reflink_extractor",
]
