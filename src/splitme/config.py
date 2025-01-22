import os
from dataclasses import dataclass
from pathlib import Path

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
    def from_yaml(cls, path: Path) -> "Config":
        """Load configuration from YAML file."""
        with open(path, encoding="utf-8") as f:
            return cls(**yaml.safe_load(f))

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration settings from environment variables."""
        config = Config()
        config.heading_level = os.getenv("SPLITME_HEADING_LEVEL", config.heading_level)
        config.output_dir = os.getenv("SPLITME_OUTPUT_DIR", config.output_dir)
        config.preserve_refs = bool(os.getenv("SPLITME_PRESERVE_REFS", "True"))
        config.add_hr = bool(os.getenv("SPLITME_ADD_HR", "True"))
        return config
