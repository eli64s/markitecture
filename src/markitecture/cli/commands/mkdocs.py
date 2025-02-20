from pathlib import Path

from pydantic import AliasChoices, BaseModel, Field, field_validator

from markitecture.generators.configs.mkdocs_yaml import MkDocsConfig
from markitecture.settings.validators import convert_to_path
from markitecture.utils.printer import RichPrinter

_printer = RichPrinter()


class MkDocsCommand(BaseModel):
    """
    Generate a basic MkDocs configuration.
    """

    docs_dir: Path = Field(
        default=Path(".markitecture/docs"),
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
        _printer.print_info(
            f"Generating MkDocs static site config for: {self.docs_dir}"
        )
        MkDocsConfig(
            docs_dir=self.docs_dir,
            site_name=self.site_name,
        ).generate_config()
        _printer.print_info(f"MkDocs config generated and saved to: {self.docs_dir}.")
