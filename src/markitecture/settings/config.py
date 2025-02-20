"""CLI settings implementated using Pydantic Settings Management."""

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from markitecture.cli.commands.config import ConfigCommand
from markitecture.cli.commands.links import CheckLinksCommand, ReferenceLinksCommand
from markitecture.cli.commands.metrics import MetricsCommand
from markitecture.cli.commands.mkdocs import MkDocsCommand
from markitecture.cli.commands.split import SplitCommand


class MarkitectureApp(BaseSettings):
    """
    Main CLI interface for markitecture.
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
    metrics: MetricsCommand | None = Field(
        default=None,
        description="Generate document readability metrics",
        validation_alias=AliasChoices("m", "metrics"),
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
        env_prefix="MARKITECTURE_",
        extra="allow",
    )
