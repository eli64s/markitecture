"""CLI command for managing configurations via YAML files."""

from pathlib import Path

import yaml
from pydantic import AliasChoices, BaseModel, Field, field_validator

from markitecture.settings.validators import convert_to_path
from markitecture.utils.printer import RichPrinter

_printer = RichPrinter()


class ConfigCommand(BaseModel):
    """
    CLI command for managing configurations via YAML files.
    """

    config_path: Path = Field(
        default=Path("markitect.yml"),
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
        from markitecture.cli.app import MarkitectureApp

        _printer.print_info(
            f"Generating default configuration file at {self.config_path}"
        )
        settings = MarkitectureApp()
        settings_dict = settings.model_dump(mode="json")

        with self.config_path.open("w", encoding="utf-8") as file:
            yaml.dump(
                settings_dict,
                file,
                default_flow_style=False,
                sort_keys=False,
            )
        _printer.print_success(
            f"Markitecture configuration file generated at: {self.config_path}"
        )

    def show_config(self) -> None:
        """Displays the current configuration settings."""
        if self.config_path.exists():
            _printer.print_debug(f"Reading configuration file: {self.config_path}")

            try:
                with self.config_path.open(encoding="utf-8") as file:
                    settings = yaml.safe_load(file)
            except yaml.YAMLError as e:
                _printer.print_error(f"Error reading configuration file: {e}")
                return

            _printer.print_key_value_table("Configuration Settings", settings)

        else:
            _printer.print_error(
                f"No configuration file found at {self.config_path}. "
                "Use '--generate' to create one."
            )
