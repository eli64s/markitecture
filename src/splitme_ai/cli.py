"""Command-line interface implementation using Pydantic settings management."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    pass

from pydantic import AliasChoices, BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from splitme_ai.logger import Logger
from splitme_ai.settings import SplitmeSettings

_logger = Logger(__name__)


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
        if self.show:
            settings = SplitmeSettings()
            _logger.info("Current splitme-ai configuration:")
            for field, value in settings.model_dump().items():
                _logger.info(f"Field: {field}, Value: {value}")

        if self.generate:
            settings = SplitmeSettings()
            if Path(".splitme.yml").exists() or Path(".splitme.yaml").exists():
                with open(".splitme.yml", "w") as f:
                    f.write(settings.model_dump_json())
                _logger.info("Generated default configuration in .splitme.yml")


class SplitCommand(BaseModel):
    """
    CLI command for splitting markdown files.
    """

    input_file: Path = Field(
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

    config: Optional[ConfigCommand] = Field(
        default=None, description="Manage configuration"
    )
    split: Optional[SplitCommand] = Field(
        default=None, description="Split markdown files"
    )
    version: bool = Field(default=False, description="Package version")

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
        str_to_bool=["true", "t", "yes", "y", "on", "1", ""],
        validate_default=True,
    )

    def cli_cmd(self) -> None:
        """Execute the appropriate command."""
        from splitme_ai import __version__

        if self.version:
            _logger.info(f"splitme-ai {__version__}")
            return
        if self.split:
            self.split.cli_cmd()
        elif self.config:
            self.config.cli_cmd()
