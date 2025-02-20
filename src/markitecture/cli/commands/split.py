from pathlib import Path

from pydantic import AliasChoices, BaseModel, Field

from markitecture.settings.validators import ExistingFilePath
from markitecture.utils.file_handler import FileHandler
from markitecture.utils.printer import RichPrinter

_printer = RichPrinter()


class SplitCommand(BaseModel):
    """
    Split a markdown file into sections based on headings.
    """

    input_file: ExistingFilePath = Field(
        ...,
        description="Path to the input markdown file.",
        validation_alias=AliasChoices("i", "input"),
    )
    output_dir: Path = Field(
        default=Path(".markitecture/docs"),
        description="Directory to save split files.",
        validation_alias=AliasChoices("o", "output"),
    )
    heading_level: str = Field(
        default="##",
        description="Heading level to split on (e.g., '#', '##').",
        validation_alias=AliasChoices("hl", "heading", "level", "heading-level"),
    )
    case_sensitive: bool = Field(
        default=False,
        description="Enable case-sensitive heading matching.",
        validation_alias=AliasChoices("cs", "case-sensitive"),
    )

    def cli_cmd(self) -> None:
        """Execute the split command."""
        from markitecture.processing.text_splitter import MarkdownTextSplitter

        _printer.print_info(f"Splitting Markdown file: {self.input_file}")
        _printer.print_info(f"Splitting on heading level: {self.heading_level}")
        splitter = MarkdownTextSplitter()
        content = FileHandler().read(self.input_file)
        # splitter.settings = self.model_dump()
        splitter.process_file(content)
        _printer.print_info(f"Split completed. Files saved to: {self.output_dir}")
