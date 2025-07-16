from markitecture.processing.text_splitter import MarkdownTextSplitter
from markitecture.settings.config import SplitConfig
from markitecture.utils.file_handler import FileHandler
from markitecture.utils.printer import RichPrinter

_printer = RichPrinter()


class SplitCommand:
    def __init__(self, args):
        self.args = args
        self.config = SplitConfig(output_dir=args.output_dir, level=args.level)

    def run(self):
        """Execute the split command."""
        _printer.print_info(f"Splitting Markdown file: {self.args.input_path}")
        _printer.print_info(f"Splitting on heading level: {self.config.level}")
        splitter = MarkdownTextSplitter()
        content = FileHandler().read(self.args.input_path)
        splitter.process_file(
            content, self.config.output_dir, f"#{'#' * int(self.config.level)}"
        )
        _printer.print_info(f"Split completed. Files saved to: {self.config.output_dir}")
