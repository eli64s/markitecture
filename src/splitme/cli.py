"""Command-line interface implementated with Pydantic Settings Management."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import AliasChoices, BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich import print
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

from splitme.generators.mkdocs.config import MkDocsConfig
from splitme.logger import Logger
from splitme.tools.markdown.link_validator import LinkValidator
from splitme.tools.markdown.reflink_converter import ReferenceLinkConverter
from splitme.utils.file_handler import FileHandler
from splitme.validators import ExistingFilePath, convert_to_path

_logger = Logger(__name__)


class ConfigCommand(BaseModel):
    """
    CLI command for managing configurations via YAML files.
    """

    config_path: Path = Field(
        default=Path("splitme.yml"),
        description="Path to the configuration file.",
        validation_alias=AliasChoices("p", "path"),
    )
    generate: bool = Field(
        default=False,
        description="Generate a default configuration file.",
        validation_alias=AliasChoices("g", "generate"),
    )
    show: bool = Field(
        default=False,
        description="Display the current configuration settings.",
        validation_alias=AliasChoices("s", "show"),
    )

    validate_fields = field_validator("config_path")(convert_to_path)

    def cli_cmd(self) -> None:
        """Execute the configuration command."""
        if self.generate:
            self.generate_config()

        if self.show:
            self.show_config()

    def generate_config(self) -> None:
        """Generates a default configuration file."""
        _logger.info(f"Generating default configuration file at {self.config_path}")
        settings = SplitmeApp()
        settings_dict = settings.model_dump(mode="json")

        with self.config_path.open("w", encoding="utf-8") as file:
            yaml.dump(
                settings_dict,
                file,
                default_flow_style=False,
                sort_keys=False,
            )
        _logger.info(f"Splitme configuration file generated: {self.config_path}")

    def show_config(self) -> None:
        """Displays the current configuration settings."""
        if self.config_path.exists():
            _logger.info(f"Reading configuration file: {self.config_path}")
            try:
                with self.config_path.open(encoding="utf-8") as file:
                    settings = yaml.safe_load(file)
            except yaml.YAMLError as e:
                _logger.error(f"Error reading configuration file: {e}")
                return

            self.display_settings(settings)
        else:
            _logger.error(
                f"No configuration file found at {self.config_path}. "
                "Use '--generate' to create one."
            )

    def display_settings(self, settings: dict[str, str]) -> None:
        """Displays settings using Rich."""
        theme = Theme({
            "title": "bold yellow",
            "header": "bold green",
            "key": "cyan",
            "value": "magenta",
        })
        console = Console(theme=theme)
        console.print("[title]Configuration Settings[/title]\n")
        table = Table(show_header=True, header_style="header")
        table.add_column("Key", style="key", no_wrap=True)
        table.add_column("Value", style="value")
        for key, value in settings.items():
            table.add_row(str(key), str(value))
        console.print(table)


class CheckLinksCommand(BaseModel):
    """
    Validate all links in a markdown file.
    """

    input_file: ExistingFilePath = Field(
        ...,
        description="Path to the markdown file.",
        validation_alias=AliasChoices("i", "input"),
    )
    report_path: Path = Field(
        default=Path(".splitme/link_health.txt"),
        description="Path to save the report.",
        validation_alias=AliasChoices("rp", "report-path"),
    )
    max_workers: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of concurrent link checks.",
        validation_alias=AliasChoices("mw", "max-workers"),
    )
    timeout: int = Field(
        default=10,
        ge=1,
        le=180,
        description="Timeout for link validation in seconds.",
        validation_alias=AliasChoices("t", "timeout"),
    )

    def cli_cmd(self) -> None:
        """Execute the check links command."""
        _logger.info(f"Scanning markdown file {self.input_file} for broken links...")

        checker = LinkValidator(timeout=self.timeout, max_workers=self.max_workers)
        results = checker.check_markdown_file(str(self.input_file))
        if not results:
            _logger.info("No links found.")
            return

        custom_theme = Theme({
            "title": "bold yellow",
            "header": "bold green",
            "field": "dim",
            "value": "bold magenta",
            "error": "bold red",
        })
        console = Console(theme=custom_theme)
        console.print("\n[title]Markdown Link Check Results[/title]\n")
        table = Table(show_header=True, header_style="header")
        table.add_column("Status", style="field")
        table.add_column("Line", style="value")
        table.add_column("Link", style="value")
        table.add_column("Error", style="error")
        broken_links = 0
        for result in results:
            status = "✓" if result["status"] == "ok" else "𝗫"
            error = result["error"] if result["error"] else ""
            table.add_row(
                status, str(result["line"]), f"[link]{result['url']}[/link]", error
            )
            if result["error"]:
                broken_links += 1
        console.print(table)
        console.print(
            f"\nSummary: {broken_links} broken links out of {len(results)} total links."
        )


class ReferenceLinksCommand(BaseModel):
    """
    Convert inline markdown links to reference-style links.
    """

    input_file: ExistingFilePath = Field(
        ...,
        description="Path to the markdown file.",
        validation_alias=AliasChoices("i", "input"),
    )
    output_file: Path | str = Field(
        default=Path("reflinks_output.md"),
        description="Path to save updated document.",
        validation_alias=AliasChoices("o", "output"),
    )

    def cli_cmd(self) -> None:
        """Execute the reference link conversion."""
        _logger.info(
            f"Converting all links in '{self.input_file}' to reference style..."
        )
        converter = ReferenceLinkConverter()
        converter.process_file(self.input_file, self.output_file or self.input_file)
        _logger.info(
            f"Link conversion complete. Updated file saved to '{self.output_file}'."
        )


class MkDocsCommand(BaseModel):
    """
    Generate a basic MkDocs configuration.
    """

    docs_dir: Path = Field(
        default=Path(".splitme/docs"),
        description="Path to the documentation directory.",
        validation_alias=AliasChoices("d", "dir", "docs-dir"),
    )
    site_name: str = Field(
        default="MkDocs Static Site Documentation",
        description="Name of the MkDocs site.",
        validation_alias=AliasChoices("name", "site-name"),
    )

    validate_fields = field_validator("docs_dir")(convert_to_path)

    def cli_cmd(self) -> None:
        """Execute MkDocs configuration generation."""
        _logger.info(f"Generating MkDocs static site config for: {self.docs_dir}")
        MkDocsConfig(
            docs_dir=self.docs_dir,
            site_name=self.site_name,
        ).generate_config()
        _logger.info(f"MkDocs config generated and saved to: {self.docs_dir}.")


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
        default=Path(".splitme/docs"),
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
        from splitme.core import MarkdownSplitter

        _logger.info(f"Splitting Markdown file: {self.input_file}")
        _logger.info(f"Splitting on heading level: {self.heading_level}")
        splitter = MarkdownSplitter()
        content = FileHandler().read(self.input_file)
        # splitter.settings = self.model_dump()
        splitter.process_file(content)
        _logger.info(f"Split completed. Files saved to: {self.output_dir}")


class SplitmeApp(BaseSettings):
    """
    Main CLI interface for splitme.
    """

    config: ConfigCommand | None = Field(
        default=None,
        description="Manage configuration settings",
        validation_alias=AliasChoices("c", "config"),
    )
    check_links: CheckLinksCommand | None = Field(
        default=None,
        description="Validate links in a markdown file",
        validation_alias=AliasChoices("cl", "check-links"),
    )
    reference_links: ReferenceLinksCommand | None = Field(
        default=None,
        description="Convert links to reference style",
        validation_alias=AliasChoices("rl", "reflinks"),
    )
    split: SplitCommand | None = Field(
        default=None,
        description="Split a markdown file into sections",
        validation_alias=AliasChoices("s", "split"),
    )
    mkdocs: MkDocsCommand | None = Field(
        default=None,
        description="Generate MkDocs configuration from a Markdown file",
        validation_alias=AliasChoices("mk", "mkdocs"),
    )
    version: bool = Field(
        default=False,
        description="Display the version number",
        validation_alias=AliasChoices("v", "version"),
    )

    model_config = SettingsConfigDict(
        case_sensitive=False,
        cli_enforce_required=False,
        cli_implicit_flags=True,
        cli_parse_args=True,
        env_prefix="SPLITME_",
        extra="allow",
    )

    def cli_cmd(self) -> None:
        """Execute the appropriate command."""

        from splitme import __version__

        if self.version:
            print(f"[bold green]splitme[/bold green] {__version__}")
            return

        if all(
            v is None
            for k, v in self.model_dump().items()
            if k
            not in [
                "version",
                "model_config",
            ]
        ):
            self.print_help()
            return

        if self.config:
            self.config.cli_cmd()
        if self.check_links:
            self.check_links.cli_cmd()
        if self.reference_links:
            self.reference_links.cli_cmd()
        if self.split:
            self.split.cli_cmd()
        if self.mkdocs:
            self.mkdocs.cli_cmd()


def main() -> None:
    """Main entry point for the Splitme CLI."""
    settings = SplitmeApp()
    settings.cli_cmd()
