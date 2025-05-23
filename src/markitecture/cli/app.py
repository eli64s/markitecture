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
        elif settings.links:
            if settings.links.check:
                settings.links.check.cli_cmd()
            elif settings.links.reflinks:
                settings.links.reflinks.cli_cmd()
            # Add a check for other link subcommands if any are added later
            # else:
            #     _printer.print_error(
            #         "No 'links' subcommand provided. Use 'check' or 'reflinks'. Use --help for more information."
            #     )
            # It might be better to rely on Pydantic's help generation for this,
            # so the else branch might not be strictly necessary if no subcommand is given.
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
