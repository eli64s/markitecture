"""Configuration management for JSON config files."""

from dataclasses import dataclass

import yaml


@dataclass
class Config:
    """
    Configuration settings for markdown text splitting.
    """

    heading_level: str = "##"
    output_dir: str = "docs"
    preserve_refs: bool = True
    add_hr: bool = True

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        """Load configuration from YAML file."""
        with open(path, encoding="utf-8") as f:
            return cls(**yaml.safe_load(f))
