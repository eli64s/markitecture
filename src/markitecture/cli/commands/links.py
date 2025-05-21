"""Commands for checking and converting markdown links."""

import asyncio # New import
import re
from pathlib import Path

from pydantic import AliasChoices, BaseModel, Field

# Updated imports for the new CrossLinksValidator and ValidatorSettings
from markitecture.processing.link_validator import CrossLinksValidator 
from markitecture.settings.validators import ExistingFilePath, ValidatorSettings
from markitecture.processing.reflink_converter import (
    ReferenceLinkConverter,
    ReferencePlacement,
)
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
            f"Starting link validation for {self.input_file}..."
        )

        # 1. Instantiate ValidatorSettings
        # Defaulting allow_external_validation to True for typical use-case.
        # Subtask mentioned default to False if no CLI, but True is more practical for a link checker.
        settings = ValidatorSettings(
            timeout=self.timeout,
            max_workers=self.max_workers,
            allow_external_validation=True, 
            # ignore_patterns can be added as a CLI option later if needed
        )

        # 2. Instantiate CrossLinksValidator
        validator = CrossLinksValidator(settings=settings)

        # 3. Run async validation
        # ExistingFilePath ensures input_file is a file.
        # base_dir is the parent directory of the input file.
        _printer.print_info(f"Scanning {self.input_file} for links...")
        try:
            asyncio.run(validator.validate_across_files_async(
                file_paths=[self.input_file], 
                base_dir=self.input_file.parent.resolve()
            ))
        except Exception as e:
            _printer.print_error(f"An error occurred during link validation: {e}")
            # Optionally, re-raise or handle more gracefully
            return

        _printer.print_info("Validation complete. Generating report...")

        # 4. Generate and print report
        report_dict = validator.generate_report()
        text_report = validator.generate_text_report(report_dict)
        
        # Using print_info for multi-line text. _printer.echo might also work.
        # RichPrinter might have better ways to display pre-formatted text.
        # For now, a simple print:
        print(text_report) # Using direct print to ensure raw text formatting is preserved.
                           # _printer.print_info might add its own formatting.

        # 5. Save report
        if self.report_path:
            try:
                _printer.print_info(f"Saving report to {self.report_path}...")
                # Ensure parent directory exists
                self.report_path.parent.mkdir(parents=True, exist_ok=True)
                validator.save_report(report_dict, self.report_path, format="text")
                _printer.print_success(f"Report saved successfully to {self.report_path}")
            except Exception as e:
                _printer.print_error(f"Failed to save report to {self.report_path}: {e}")
        
        # Summary from report_dict
        summary = report_dict.get("summary", {})
        invalid_links_count = summary.get("invalid_links", 0)
        if invalid_links_count > 0:
            _printer.print_warning(f"Found {invalid_links_count} invalid links.")
        else:
            _printer.print_success("No invalid links found.")


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
