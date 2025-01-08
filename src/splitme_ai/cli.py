"""Command-line interface implementation using Pydantic settings management."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Set

if TYPE_CHECKING:
    pass

from pydantic import AfterValidator, AliasChoices, BaseModel, Field
from pydantic_settings import BaseSettings, CliImplicitFlag, SettingsConfigDict

from splitme_ai.generators.mkdocs_config import MkDocsConfig
from splitme_ai.logger import Logger
from splitme_ai.tools.markdown_link_converter import MarkdownLinkConverter
from splitme_ai.tools.markdown_link_validator import MarkdownLinkValidator

_logger = Logger(__name__)


def validate_path(v: Path) -> Path:
    """Check if the path exists and is a file."""
    if not v.exists():
        raise ValueError(f"Path '{v}' does not exist.")
    if not v.is_file():
        raise ValueError(f"Path '{v}' is not a file.")
    return v


# Reusable custom type with validation
ExistingFilePath = Annotated[Path, AfterValidator(validate_path)]


class SplitmeSettings(BaseSettings):
    """
    Configuration settings for splitme-ai.
    """

    case_sensitive: bool = Field(
        default=False, description="Use case-sensitive heading matching"
    )
    exclude_patterns: Set[str] = Field(
        default_factory=set, description="Patterns to exclude from splitting"
    )
    generate_mkdocs: CliImplicitFlag[bool] = Field(
        default=False,
        description="Generate MkDocs configuration",
        validation_alias=AliasChoices("mk", "mkdocs"),
    )
    heading_level: str = Field(
        default="##",
        description="Heading level to split on (e.g., '#', '##', '###')",
        validation_alias=AliasChoices("hl", "heading_level"),
    )
    output_dir: Path = Field(
        default=Path(".splitme-ai/output"),
        description="Output directory for split files",
        validation_alias=AliasChoices("o", "output"),
    )
    preserve_context: bool = Field(
        default=True, description="Preserve parent heading context in split files"
    )

    model_config = SettingsConfigDict(
        case_sensitive=False,
        cli_implicit_flags=True,
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="SPLITME_",
        extra="ignore",
        validate_default=True,
    )

    def process_mkdocs(self) -> None:
        """Generate MkDocs configuration file if enabled."""
        if not self.generate_mkdocs:
            return
        config = MkDocsConfig(
            docs_dir=self.output_dir,
            site_name=f"MkDocs Site: {self.output_dir.name}",
            enable_material=True,
        )
        config.generate_config()


class ConfigCommand(BaseModel):
    """
    CLI command for managing configurations via JSON files.
    """

    generate: bool = Field(
        default=False, description="Generate default configuration file."
    )
    show: bool = Field(
        default=False, description="Show current configuration settings."
    )

    def cli_cmd(self) -> None:
        """Execute the config command."""
        if self.generate:
            settings = SplitmeSettings()
            config_path = Path(".splitme.yml")
            if config_path.exists() or config_path.with_suffix(".yaml").exists():
                with open(".splitme.yml", "w") as f:
                    f.write(settings.model_dump_json())
                _logger.info("Generated default configuration in .splitme.yml")

        if self.show:
            settings = SplitmeSettings()
            print("\nCurrent configuration settings:")
            print("-" * 32)
            max_field_len = max(len(field) for field in settings.model_dump())
            for field, value in settings.model_dump().items():
                print(f"{field:<{max_field_len}} = {value}")
            print()


class LinkValidatorCommand(BaseModel):
    """
    CLI command for checking if Markdown links are valid.
    """

    input_file: ExistingFilePath = Field(
        ...,
        description="Input markdown file to process",
        validation_alias=AliasChoices("i", "input"),
    )
    timeout: int = Field(
        default=10,
        description="Timeout in seconds for each HTTP request",
    )
    max_workers: int = Field(
        default=5,
        description="Maximum number of concurrent requests",
    )

    model_config = SettingsConfigDict(validate_default=True, extra="forbid")

    def cli_cmd(self) -> None:
        """Execute the check links command."""
        print(f"Scanning markdown file {self.input_file} for broken links...")

        checker = MarkdownLinkValidator(
            timeout=self.timeout, max_workers=self.max_workers
        )
        results = checker.check_markdown_file(str(self.input_file))

        if not results:
            print("No links found.")
            return

        print("\nMarkdown Link Check Results:")
        print("-" * 80)

        broken_links = 0
        for result in results:
            status = "✓" if result["status"] == "ok" else "𝗫"
            print(
                f"{status} Line {result['line']}: [{result['text']}]({result['url']})"
            )
            if result["error"]:
                print(f"   Error: {result['error']}")
                broken_links += 1

        print(
            f"\nSummary: {broken_links} broken links out of {len(results)} total links."
        )


class LinkConverterCommand(BaseModel):
    """
    CLI command for converting markdown links to reference-style links.
    """

    input_file: ExistingFilePath = Field(
        ...,
        description="Input markdown file to process",
        validation_alias=AliasChoices("i", "input"),
    )
    output_file: Path | None = Field(
        default=None,
        description="Output file path (defaults to input file)",
        validation_alias=AliasChoices("o", "output"),
    )

    model_config = SettingsConfigDict(validate_default=True, extra="forbid")

    def cli_cmd(self) -> None:
        """Execute the reference links command."""
        converter = MarkdownLinkConverter()
        _logger.info(f"Converting all links in {self.input_file} to reference-style.")
        converter.process_file(self.input_file, self.output_file)
        _logger.info(f"Output written to {self.output_file}")


class SplitCommand(BaseModel):
    """
    CLI command for splitting markdown files.
    """

    input_file: ExistingFilePath = Field(
        ...,
        description="Input markdown file to split",
        validation_alias=AliasChoices("i", "input"),
    )
    settings: SplitmeSettings = Field(
        default_factory=SplitmeSettings,
        description="Configuration settings for text splitting.",
    )

    def cli_cmd(self) -> None:
        """Execute the split command."""
        from splitme_ai.core import MarkdownSplitter

        splitter = MarkdownSplitter(self.settings)
        content = self.input_file.read_text(encoding="utf-8")
        sections = splitter.process_file(content)

        _logger.info(f"Split {self.input_file} into {len(sections)} sections.")

        for section in sections:
            _logger.info(f"Created file {section.filename} from {section.title}")


class SplitmeApp(BaseSettings):
    """
    Main application CLI interface.
    """

    config: ConfigCommand | None = Field(
        default=None, description="Manage configuration"
    )
    split: SplitCommand | None = Field(
        default=None,
        description="Split markdown files",
        validation_alias=AliasChoices("s", "split"),
    )
    reference_links: LinkConverterCommand | None = Field(
        default=None,
        description="Convert all links to reference-style syntax",
        validation_alias=AliasChoices("rl", "reflinks"),
    )
    validate_links: LinkValidatorCommand | None = Field(
        default=None,
        description="Check if links in a markdown file are valid",
        validation_alias=AliasChoices("vl", "validate-links"),
    )
    version: bool = Field(
        default=False,
        description="Package version",
        validation_alias=AliasChoices("v", "V", "version"),
    )

    model_config = SettingsConfigDict(
        case_sensitive=True,
        cli_enforce_required=True,
        cli_kebab_case=True,
        cli_implicit_flags=True,
        cli_parse_args=True,
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="SPLITME_",
        protected_namespaces=(),
        # str_to_bool=["true", "t", "yes", "y", "on", "1", ""],
        validate_default=True,
    )

    def cli_cmd(self) -> None:
        """Execute the appropriate command."""
        from splitme_ai import __version__

        if self.version:
            print(f"splitme-ai version {__version__}")
            return
        if self.split:
            self.split.cli_cmd()
        elif self.config:
            self.config.cli_cmd()
        elif self.reference_links:
            self.reference_links.cli_cmd()
        elif self.validate_links:
            self.validate_links.cli_cmd()
