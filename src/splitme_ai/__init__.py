from importlib.metadata import version

from splitme_ai.config import Config as Config
from splitme_ai.core import MarkdownSplitter as MarkdownSplitter
from splitme_ai.errors import FileOperationError as FileOperationError
from splitme_ai.errors import ParseError as ParseError
from splitme_ai.errors import SplitmeAIBaseError
from splitme_ai.utils.file_handler import FileHandler

__version__ = version("splitme-ai")

__all__: list[str] = [
    "Config",
    "FileHandler",
    "FileOperationError",
    "MarkdownSplitter",
    "ParseError",
    "SplitmeAIBaseError",
]
