"""Enhanced terminal output formatting with integrated table titles."""

from typing import List, Optional

from rich.box import ROUNDED, SIMPLE
from rich.console import Console
from rich.table import Table
from rich.theme import Theme


class RichPrinter:
    """
    Utility class for Rich-based printing with integrated table titles and clickable links.
    """

    def __init__(self) -> None:
        """Initialize the RichPrinter with a custom theme and console."""
        self.theme = Theme({
            "info": "cyan",
            "success": "bold green",
            "error": "bold red",
            "warning": "yellow",
            "header": "bold blue",
            "title": "bold magenta",
            "key": "bold white",
            "value": "dim",
            "table_title": "bold white on blue",
        })
        self.console = Console(theme=self.theme)

    # -------------------------------------------------------------------------
    # Basic text-level messages
    # -------------------------------------------------------------------------
    def print_debug(self, message: str) -> None:
        """Print a debug message."""
        self.console.print(f"[dim]{message}[/dim]")

    def print_info(self, message: str) -> None:
        """Print an informational message."""
        self.console.print(f"[info]{message}[/info]")

    def print_success(self, message: str) -> None:
        """Print a success message."""
        self.console.print(f"[success]{message}[/success]")

    def print_error(self, message: str) -> None:
        """Print an error message."""
        self.console.print(f"[error]{message}[/error]")

    def print_warning(self, message: str) -> None:
        """Print a warning message."""
        self.console.print(f"[warning]{message}[/warning]")

    def print_title(self, title: str) -> None:
        """Print a styled title."""
        self.console.print(f"[title]{title}[/title]")

    def print_version(self, version: str) -> None:
        """Print a styled version number."""
        package_name = __package__.split(".")[0]
        self.console.print(f"[bold green]{package_name}[/bold green] {version}")

    # -------------------------------------------------------------------------
    # Table printing methods
    # -------------------------------------------------------------------------
    def print_key_value_table(self, title: str, data: dict[str, str]) -> None:
        """
        Print a table with integrated title and key-value pairs.

        Args:
            title: The title of the table
            data: A dictionary of key-value pairs to display
        """
        # Main container with no border
        main_table = Table(box=None, show_header=False, show_edge=False, padding=0)
        main_table.add_column("content", ratio=1)

        # Title sub-table
        title_table = Table(box=SIMPLE, show_header=False, padding=(0, 1))
        title_table.add_column("title", style="table_title", ratio=1)
        title_table.add_row(title)

        # Content sub-table for key-value pairs
        content_table = Table(box=ROUNDED, show_header=False, padding=(0, 1))
        content_table.add_column("Key", style="key", no_wrap=True)
        content_table.add_column("Value", style="value")

        # Add data rows
        for key, val in data.items():
            content_table.add_row(key, val)

        main_table.add_row(title_table)
        main_table.add_row(content_table)

        self.console.print()
        self.console.print(main_table)
        self.console.print()

    def print_table(
        self, title: str, headers: List[str], rows: List[List[str]]
    ) -> None:
        """
        Print a custom table with integrated title.

        Args:
            title: The title of the table
            headers: List of column headers
            rows: List of row data, each row being a list of strings
        """
        # Main container
        main_table = Table(box=None, show_header=False, show_edge=False, padding=0)
        main_table.add_column("content", ratio=1)

        # Title sub-table
        title_table = Table(box=SIMPLE, show_header=False, padding=(0, 1))
        title_table.add_column("title", style="table_title", ratio=1)
        title_table.add_row(title)

        # Content table
        content_table = Table(
            box=ROUNDED, show_header=True, header_style="bold blue", padding=(0, 1)
        )

        for header in headers:
            content_table.add_column(header, style="key")

        for row in rows:
            content_table.add_row(*row)

        main_table.add_row(title_table)
        main_table.add_row(content_table)

        self.console.print()
        self.console.print(main_table)
        self.console.print()

    def print_link_table(
        self, title: str, link_rows: List[dict], columns: Optional[List[str]] = None
    ) -> None:
        """
        Print a table specifically for link data, allowing clickable URLs.

        Each element in link_rows is expected to be a dict with
        keys like 'line', 'url', 'status', 'error' (depending on your link checking code).

        Args:
            title: The table title
            link_rows: A list of dicts representing link info. Must have 'url' at least.
            columns: Optional list of columns to display in table order.
                     If None, uses ["line", "status", "url", "error"] by default.
        """
        if columns is None:
            columns = ["line", "status", "url", "error"]

        # Create main container
        main_table = Table(box=None, show_header=False, show_edge=False, padding=0)
        main_table.add_column("content", ratio=1)

        # Title sub-table
        title_table = Table(box=SIMPLE, show_header=False, padding=(0, 1))
        title_table.add_column("title", style="table_title", ratio=1)
        title_table.add_row(title)

        # Content table
        content_table = Table(
            box=ROUNDED,
            show_header=True,
            header_style="bold blue",
            padding=(0, 1),
            collapse_padding=True,
        )

        # Add columns
        for col in columns:
            content_table.add_column(col.capitalize(), style="key")

        # Add rows
        for row_data in link_rows:
            row_values = []
            for col in columns:
                val = row_data.get(col, "")
                if col == "url" and isinstance(val, str) and val.startswith("http"):
                    # Make it clickable in the terminal
                    link_text = f"[link={val}]{val}[/link]"
                    row_values.append(link_text)
                else:
                    row_values.append(str(val))
            content_table.add_row(*row_values)

        main_table.add_row(title_table)
        main_table.add_row(content_table)

        self.console.print()
        self.console.print(main_table)
        self.console.print()
