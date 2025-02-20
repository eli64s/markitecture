from importlib.metadata import version

from markitecture import metrics

from .errors import (
    FileOperationError,
    FileReadError,
    FileWriteError,
    InvalidPathError,
    MarkitectureBaseError,
    ParseError,
)
from .generators.configs.mkdocs_yaml import MkDocsConfig
from .metrics.svg_generator import MetricsSvgGenerator
from .processing.reflink_converter import (
    ReferenceLinkConverter,
    ReferencePlacement,
)
from .processing.text_splitter import MarkdownTextSplitter
from .utils.file_handler import FileHandler
from .utils.printer import RichPrinter

__version__ = version("markitecture")

__all__: list[str] = [
    "FileHandler",
    "FileOperationError",
    "FileReadError",
    "FileWriteError",
    "InvalidPathError",
    "MarkdownTextSplitter",
    "MarkitectureBaseError",
    "MetricsSvgGenerator",
    "MkDocsConfig",
    "ParseError",
    "ReferenceLinkConverter",
    "ReferencePlacement",
    "RichPrinter",
    "__version__",
    "metrics",
]
