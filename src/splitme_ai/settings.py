"""Pydantic settings management for the splitme-ai package."""

from pathlib import Path
from typing import Set

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, CliImplicitFlag, SettingsConfigDict

from splitme_ai.generators.mkdocs_config import MkDocsConfig


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
