import asyncio
import re
from pathlib import Path

from markitecture.processing.link_validator import CrossLinksValidator
from markitecture.processing.reflink_converter import (
    ReferenceLinkConverter,
    ReferencePlacement,
)
from markitecture.settings.config import LinksConfig
from markitecture.settings.validators import ValidatorSettings
from markitecture.utils.printer import RichPrinter

_printer = RichPrinter()


class LinksCommand:
    def __init__(self, args):
        self.args = args
        self.config = LinksConfig()

    def run(self):
        if self.args.links_command == "check":
            self.check_links()
        elif self.args.links_command == "reflinks":
            self.convert_reflinks()

    def check_links(self):
        """Execute the check links command."""
        _printer.print_info(f"Starting link validation for {self.args.path}...")

        settings = ValidatorSettings(
            timeout=self.config.request_timeout,
            max_workers=5,
            allow_external_validation=True,
            ignore_patterns=self.config.ignore_domains,
        )

        validator = CrossLinksValidator(settings=settings)

        try:
            asyncio.run(
                validator.validate_across_files_async(
                    file_paths=[Path(self.args.path)],
                    base_dir=Path(self.args.path).parent.resolve(),
                )
            )
        except Exception as e:
            _printer.print_error(f"An error occurred during link validation: {e}")
            return

        _printer.print_info("Validation complete. Generating report...")

        report_dict = validator.generate_report()
        text_report = validator.generate_text_report(report_dict)

        print(text_report)

        summary = report_dict.get("summary", {})
        invalid_links_count = summary.get("invalid_links", 0)
        if invalid_links_count > 0:
            _printer.print_warning(f"Found {invalid_links_count} invalid links.")
        else:
            _printer.print_success("No invalid links found.")

    def convert_reflinks(self):
        """Execute the reference link conversion."""
        _printer.print_title("Reference Link Conversion")
        _printer.print_info("Configuration:")
        _printer.print_key_value_table(
            "Settings",
            {
                "Input File": str(self.args.path),
                "Output File": f"{self.args.path} (in-place)",
                "Placement": "end",
            },
        )

        try:
            converter = ReferenceLinkConverter()
            content = Path(self.args.path).read_text()

            initial_links = len(re.findall(r"\[([^\]]+)\]\(([^\)]+)\)", content))
            _printer.print_info(f"Found {initial_links} inline links to convert")

            _printer.print_debug("Starting conversion process...")
            converter.process_file(
                self.args.path,
                None,
                ReferencePlacement.END,
            )

            result = Path(self.args.path).read_text()
            final_refs = len(re.findall(r"^\[[^\]]+\]:", result, re.MULTILINE))

            _printer.print_success("\nConversion Summary:")
            _printer.print_key_value_table(
                "Results",
                {
                    "Links Processed": str(initial_links),
                    "References Created": str(final_refs),
                    "Output Location": str(self.args.path),
                },
            )

        except Exception as e:
            _printer.print_error(f"Error during conversion: {e!s}")
            raise
