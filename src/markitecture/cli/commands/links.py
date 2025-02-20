"""Commands for checking and converting markdown links."""

import re
from pathlib import Path

from pydantic import AliasChoices, BaseModel, Field

from markitecture.processing.link_validator import LinkValidator
from markitecture.processing.reflink_converter import (
    ReferenceLinkConverter,
    ReferencePlacement,
)
from markitecture.settings.validators import ExistingFilePath
from markitecture.utils.printer import RichPrinter

_printer = RichPrinter()


class CheckLinksCommand(BaseModel):
    """
    Validate all links in a markdown file.
    """

    input_file: ExistingFilePath = Field(
        ...,
        description="Path to the markdown file.",
        validation_alias=AliasChoices("i", "input"),
    )
    report_path: Path = Field(
        default=Path(".markitecture/link_health.txt"),
        description="Path to save the report.",
        validation_alias=AliasChoices("rp", "report-path"),
    )
    max_workers: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of concurrent link checks.",
        validation_alias=AliasChoices("mw", "max-workers"),
    )
    timeout: int = Field(
        default=10,
        ge=1,
        le=180,
        description="Timeout for link validation in seconds.",
        validation_alias=AliasChoices("t", "timeout"),
    )

    def cli_cmd(self) -> None:
        """Execute the check links command."""
        _printer.print_info(
            f"Scanning markdown file {self.input_file} for broken links..."
        )

        checker = LinkValidator(timeout=self.timeout, max_workers=self.max_workers)
        results = checker.check_markdown_file(str(self.input_file))
        if not results:
            _printer.print_info("No links found.")
            return

        broken_links = 0
        rows = []
        for result in results:
            status = "✓" if result["status"] == "ok" else "𝗫"
            error = result["error"] if result["error"] else ""
            rows.append([status, str(result["line"]), result["url"], error])
            if result["error"]:
                broken_links += 1

        _printer.print_table(
            "Markdown Link Check Results",
            ["Status", "Line", "Link", "Error"],
            rows,
        )
        _printer.print_success(
            f"Summary: {broken_links} broken links out of {len(results)} total links.\n"
        )


class ReferenceLinksCommand(BaseModel):
    """Convert inline markdown links to reference-style links."""

    input_file: ExistingFilePath = Field(
        ...,
        description="Path to the markdown file.",
        validation_alias=AliasChoices("i", "input"),
    )
    output_file: Path | str = Field(
        default=Path("reflinks_output.md"),
        description="Path to save updated document.",
        validation_alias=AliasChoices("o", "output"),
    )
    placement: ReferencePlacement = Field(
        default=ReferencePlacement.END,
        description="Where to place reference links (end/section).",
        validation_alias=AliasChoices("p", "placement"),
    )

    def cli_cmd(self) -> None:
        """Execute the reference link conversion."""
        _printer.print_title("Reference Link Conversion")
        _printer.print_info("Configuration:")
        _printer.print_key_value_table(
            "Settings",
            {
                "Input File": str(self.input_file),
                "Output File": str(self.output_file),
                "Placement": self.placement.value,
            },
        )

        try:
            # Initialize converter
            converter = ReferenceLinkConverter()
            content = Path(self.input_file).read_text()

            # Extract initial metrics
            initial_links = len(re.findall(r"\[([^\]]+)\]\(([^\)]+)\)", content))
            _printer.print_info(f"Found {initial_links} inline links to convert")

            # Process file
            _printer.print_debug("Starting conversion process...")
            converter.process_file(
                self.input_file,
                self.output_file or self.input_file,
                self.placement,
            )

            # Get final metrics
            result = Path(self.output_file).read_text()
            final_refs = len(re.findall(r"^\[[^\]]+\]:", result, re.MULTILINE))

            # Summary
            _printer.print_success("\nConversion Summary:")
            _printer.print_key_value_table(
                "Results",
                {
                    "Links Processed": str(initial_links),
                    "References Created": str(final_refs),
                    "Output Location": str(self.output_file),
                },
            )

        except Exception as e:
            _printer.print_error(f"Error during conversion: {e!s}")
            raise
