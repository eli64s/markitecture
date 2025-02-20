from markitecture.settings.config import MarkitectureApp
from markitecture.utils.printer import RichPrinter

_printer = RichPrinter()


def run_cli() -> None:
    """
    Main entry point for the CLI. Routes commands to their appropriate handlers.
    """
    from markitecture import __version__

    try:
        settings = MarkitectureApp()
        if settings.version:
            _printer.print_version(__version__)
            return

        if settings.config:
            settings.config.cli_cmd()
        elif settings.check_links:
            settings.check_links.cli_cmd()
        elif settings.reference_links:
            settings.reference_links.cli_cmd()
        elif settings.metrics:
            settings.metrics.cli_cmd()
        elif settings.mkdocs:
            settings.mkdocs.cli_cmd()
        elif settings.split:
            settings.split.cli_cmd()
        else:
            _printer.print_error(
                "No command provided. Use `--help` for more information."
            )

    except Exception as e:
        _printer.print_error(f"An error occurred: {e!r}")
        raise e
