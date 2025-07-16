from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SplitConfig(BaseSettings):
    """Configuration for the split command."""

    output_dir: Path = Field(..., help="Output directory for split files.")
    level: str = Field(default="##", help='Heading level to split on (e.g., "##", "###").')
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")

    model_config = SettingsConfigDict(cli_parse_args=False)


class LinksConfig(BaseSettings):
    """Configuration for the links command."""

    request_timeout: int = Field(default=10, description="Timeout in seconds for HTTP requests.")
    ignore_domains: list[str] = Field(default_factory=list, description="List of domains to ignore.")

    model_config = SettingsConfigDict(cli_parse_args=False)
