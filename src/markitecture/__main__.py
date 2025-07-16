import argparse
import sys

from markitecture.cli.commands.links import LinksCommand
from markitecture.cli.commands.split import SplitCommand


def main():
    parser = argparse.ArgumentParser(
        prog="markitecture",
        description="A collection of tools for managing and enhancing your markdown documentation.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Split command
    split_parser = subparsers.add_parser("split", help="Split a markdown file into smaller chunks.")
    split_parser.add_argument("input_path", help="Path to the markdown file to split.")
    split_parser.add_argument("output_dir", help="Directory to save the split files.")
    split_parser.add_argument(
        "--level",
        type=int,
        default=2,
        help="The markdown heading level to split by.",
    )
    split_parser.set_defaults(func=SplitCommand)

    # Links command
    links_parser = subparsers.add_parser("links", help="Commands for managing links.")
    links_subparsers = links_parser.add_subparsers(dest="links_command", help="Link commands")

    # Links check command
    links_check_parser = links_subparsers.add_parser("check", help="Check for broken links in a markdown file.")
    links_check_parser.add_argument("path", help="Path to the markdown file or directory to check.")
    links_check_parser.set_defaults(func=LinksCommand)

    # Links reflinks command
    links_reflinks_parser = links_subparsers.add_parser("reflinks", help="Convert reference links to absolute links.")
    links_reflinks_parser.add_argument("path", help="Path to the markdown file or directory to convert.")
    links_reflinks_parser.set_defaults(func=LinksCommand)

    args = parser.parse_args()

    if hasattr(args, "func"):
        command = args.func(args)
        command.run()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
