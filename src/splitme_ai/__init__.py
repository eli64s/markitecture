from splitme_ai.config import Config as Config
from splitme_ai.core import MarkdownSplitter as MarkdownSplitter
from splitme_ai.errors import FileOperationError as FileOperationError
from splitme_ai.errors import ParseError as ParseError
from splitme_ai.errors import SplitmeAIBaseError

__version__ = "0.1.0"

__all__: list[str] = [
    "Config",
    "FileOperationError",
    "MarkdownSplitter",
    "ParseError",
    "SplitmeAIBaseError",
]
