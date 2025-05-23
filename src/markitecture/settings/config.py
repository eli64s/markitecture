"""CLI settings implementated using Pydantic Settings Management."""

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from markitecture.cli.commands.config import ConfigCommand
from markitecture.cli.commands.links import CheckLinksCommand, ReferenceLinksCommand
from markitecture.cli.commands.metrics import MetricsCommand
from markitecture.cli.commands.mkdocs import MkDocsCommand
from markitecture.cli.commands.split import SplitCommand


class LinksGroupCommand(BaseSettings):
    """Commands for link management."""

    check: CheckLinksCommand | None = Field(
        default=None,
        description="Validate links in a markdown file.",
        validation_alias=AliasChoices("ck", "check"),
    )
    reflinks: ReferenceLinksCommand | None = Field(
        default=None,
        description="Convert inline links to reference-style links.",
        validation_alias=AliasChoices("rf", "reflinks"),
    )
    # Add model_config if necessary, similar to MarkitectureApp,
    # to ensure subcommands are parsed correctly.
    # E.g., model_config = SettingsConfigDict(cli_parse_args=True, extra="allow")
    # However, often Pydantic handles nested parsing automatically.
    # Let's try without it first.


class MarkitectureApp(BaseSettings):
    """
    Main CLI interface for markitecture.
    """

    config: ConfigCommand | None = Field(
        default=None,
        description="Manage configuration settings",
        validation_alias=AliasChoices("c", "config"),
    )
    links: LinksGroupCommand | None = Field(
        default=None,
        description="Manage and convert document links.",
        validation_alias=AliasChoices("ln", "links"),
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
