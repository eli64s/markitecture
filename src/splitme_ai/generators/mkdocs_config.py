import re
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Set,
    Union,
)

import yaml

from splitme_ai.errors import FileOperationError
from splitme_ai.utils.file_handler import FileHandler


class MkDocsConfig:
    """
    Handles MkDocs configuration generation.
    """

    # Define priority pages that should appear first in navigation
    PRIORITY_PAGES: ClassVar[List[str]] = [
        "readme",
        "index",
        "introduction",
        "getting-started",
        "quick-start",
    ]

    def __init__(
        self,
        docs_dir: Union[str, Path] = ".splitme-ai/",
        site_name: str = "MkDocs Site Documentation",
        enable_material: bool = True,
        theme_palette: Optional[Dict[str, str]] = None,
    ) -> None:
        if not site_name or not site_name.strip():
            raise ValueError("Site name cannot be empty")

        self.docs_dir = Path(docs_dir)
        if not self.docs_dir.exists() and not self.docs_dir.parent.exists():
            raise ValueError(f"Invalid documentation directory path: {docs_dir}")

        self.site_name = site_name.strip()
        self.enable_material = enable_material
        self.theme_palette = theme_palette or {
            "scheme": "default",
            "primary": "indigo",
            "accent": "indigo",
        }
        self.file_handler = FileHandler()

    def _format_nav_title(self, filename: str) -> str:
        """Format a filename into a readable navigation title.

        Args:
            filename: Name of the markdown file without extension

        Returns:
            Formatted title suitable for navigation
        """
        # Remove common prefix/suffix patterns
        clean_name = re.sub(r"^[0-9]+[-_]", "", filename)
        clean_name = re.sub(r"[-_]?index$", "", clean_name)

        # Replace separators and capitalize
        return clean_name.replace("-", " ").replace("_", " ").strip().title()

    def _generate_nav(self) -> List[Dict[str, str]]:
        """Generate organized navigation structure from markdown files.

        Returns:
            List of navigation items with priority-based ordering

        Raises:
            FileOperationError: If there are issues accessing or reading files
        """
        nav: List[Dict[str, str]] = []
        try:
            # Ensure the docs directory exists
            self.docs_dir.mkdir(parents=True, exist_ok=True)

            # Get all markdown files
            md_files = list(self.docs_dir.glob("*.md"))
            if not md_files:
                raise FileOperationError(f"No markdown files found in {self.docs_dir}")

            # Sort files into priority and regular lists
            priority_files: List[Path] = []
            regular_files: List[Path] = []

            for md_file in md_files:
                if md_file.stem.lower() in self.PRIORITY_PAGES:
                    priority_files.append(md_file)
                else:
                    regular_files.append(md_file)

            # Add priority files first, in order specified in PRIORITY_PAGES
            for page in self.PRIORITY_PAGES:
                matching_files = [f for f in priority_files if f.stem.lower() == page]
                if matching_files:
                    title = (
                        "Home"
                        if page in ["readme", "index"]
                        else self._format_nav_title(page)
                    )
                    nav.append({
                        title: str(matching_files[0].relative_to(self.docs_dir))
                    })

            # Add remaining files alphabetically
            for md_file in sorted(regular_files, key=lambda x: x.stem.lower()):
                title = self._format_nav_title(md_file.stem)
                nav.append({title: str(md_file.relative_to(self.docs_dir))})

        except Exception as e:
            raise FileOperationError(
                f"Failed to generate navigation structure: {e!s}"
            ) from e

        return nav

    def _get_base_config(self) -> Dict[str, Union[str, Dict[str, str]]]:
        """Get comprehensive MkDocs configuration with enhanced theme settings.

        Returns:
            Complete MkDocs configuration dictionary
        """
        config = {
            "site_name": self.site_name,
            "docs_dir": str(self.docs_dir),
            "nav": self._generate_nav(),
        }

        if self.enable_material:
            config.update({
                "theme": {
                    "name": "material",
                    "palette": self.theme_palette,
                    "features": [
                        "navigation.instant",
                        "navigation.tracking",
                        "navigation.tabs",
                        "navigation.sections",
                        "navigation.expand",
                        "search.highlight",
                    ],
                },
                "markdown_extensions": [
                    "admonition",
                    "pymdownx.details",
                    "pymdownx.superfences",
                    "pymdownx.highlight",
                    "pymdownx.inlinehilite",
                    "pymdownx.snippets",
                    "tables",
                    "footnotes",
                ],
            })

        return config

    def generate_config(
        self,
        output_file: Optional[Union[str, Path]] = None,
        extra_config: Optional[Dict[str, Union[str, Dict[str, str]]]] = None,
    ) -> None:
        """Generate MkDocs configuration file with enhanced error handling.

        Args:
            output_file: Path for configuration file output
            extra_config: Additional configuration options to include

        Raises:
            FileOperationError: If configuration file cannot be written
            ValueError: If output_file is invalid
        """
        if not output_file:
            output_file = self.docs_dir / "mkdocs.yml"

        config = self._get_base_config()

        # Merge any extra configuration settings
        if extra_config:
            config = self._deep_merge_configs(config, extra_config)

        try:
            # Ensure parent directories exist
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with output_path.open("w", encoding="utf-8") as file:
                yaml.dump(
                    config,
                    file,
                    Dumper=SpacedDumper,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                    indent=2,  # Ensure consistent indentation
                )

        except Exception as e:
            raise FileOperationError(
                f"Failed to write MkDocs configuration to {output_file}: {e!s}"
            ) from e

    def _deep_merge_configs(self, base: dict, update: dict) -> dict:
        """Recursively merge two configuration dictionaries.

        Args:
            base: Base configuration dictionary
            update: Update configuration dictionary

        Returns:
            Merged configuration dictionary
        """
        result = base.copy()
        for key, value in update.items():
            if (
                isinstance(value, dict)
                and key in result
                and isinstance(result[key], dict)
            ):
                result[key] = self._deep_merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def update_nav(self, output_file: Union[str, Path] = "mkdocs.yml") -> None:
        """Update navigation while preserving other configuration settings.

        Args:
            output_file: Path to existing MkDocs configuration file

        Raises:
            FileOperationError: If config file cannot be accessed
            FileNotFoundError: If config file does not exist
        """
        output_path = Path(output_file)
        if not output_path.exists():
            raise FileNotFoundError(f"Config file not found: {output_file}")

        try:
            # Read existing configuration
            with output_path.open("r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Update navigation structure
            config["nav"] = self._generate_nav()

            # Write updated configuration
            with output_path.open("w", encoding="utf-8") as file:
                yaml.dump(
                    config,
                    file,
                    Dumper=SpacedDumper,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                    indent=2,  # Ensure consistent indentation
                )

        except Exception as e:
            raise FileOperationError(
                f"Failed to update navigation in {output_file}: {e!s}"
            ) from e


class SpacedDumper(yaml.Dumper):
    """
    Custom YAML dumper that adds spacing between major configuration sections.

    This dumper ensures that the generated YAML config is more readable by:
    - Keeping basic settings grouped together at the top
    - Adding line breaks between major sections like nav, theme, and extensions
    - Maintaining proper indentation throughout
    """

    # Settings that should be grouped together at the top without extra spacing
    BASIC_SETTINGS: ClassVar[Set[str]] = {
        "site_name",
        "docs_dir",
        "site_url",
        "repo_url",
        "repo_name",
    }

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.last_was_basic = False
        self.current_key: Optional[str] = None

    def represent_mapping(
        self,
        tag: str,
        mapping: Any,  # Union[SupportsItems[Any, Any], Iterable[tuple[Any, Any]]],
        flow_style: Optional[bool] = None,
    ) -> yaml.MappingNode:
        """Override to track the current key being processed."""
        # Get the key if we're at the top level
        if len(self.indents) == 0 and mapping:
            self.current_key = next(iter(mapping))  # type: ignore
        return super().represent_mapping(tag, mapping, flow_style)

    def write_line_break(self, data: Optional[str] = None) -> None:
        """Add extra line breaks between major sections, but not basic settings."""
        super().write_line_break(data)

        # Only add extra spacing for top-level items that aren't basic settings
        if (
            len(self.indents) == 1
            and self.current_key not in self.BASIC_SETTINGS
            and not self.last_was_basic
        ):
            super().write_line_break()

        # Track whether we just processed a basic setting
        self.last_was_basic = (
            len(self.indents) == 1 and self.current_key in self.BASIC_SETTINGS
        )
