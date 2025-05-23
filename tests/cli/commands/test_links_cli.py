"""Test suite for CLI 'links reflinks' command."""

import subprocess
import sys
from pathlib import Path

import pytest

# Sample markdown strings (copied from test_reflink_converter.py for simplicity)
sample_md_inline_links = """
# My Document

This is a paragraph with an [inline link to Google](https://www.google.com).
Here is another [link to OpenAI](https://www.openai.com) in the same paragraph.

Another paragraph with a [link to Pydantic's documentation](https://docs.pydantic.dev/).
And an image: ![alt text for image](images/my_image.png)
"""

sample_md_with_sections = """
# Chapter 1

Some text with [an inline link](https://example.com/page1).

## Section 1.1

More text and [another link](https://example.com/page2) for this section.

# Chapter 2

Text for chapter 2, including a [third link](https://example.com/page3).
"""


@pytest.fixture
def create_temp_md_file(tmp_path: Path):
    """Fixture to create a temporary markdown file with given content."""
    def _create_file(filename: str, content: str) -> Path:
        file_path = tmp_path / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path
    return _create_file


def run_markitect_cli(args: list[str]) -> subprocess.CompletedProcess:
    """Helper function to run the Markitecture CLI."""
    # Assumes markitecture can be run as a module: python -m markitecture
    command = [sys.executable, "-m", "markitecture"] + args
    # Setting CWD to ensure that if the CLI tries to access relative paths for
    # non-file-input things (like default report paths), it's consistent.
    # For these tests, all file paths are absolute via tmp_path.
    return subprocess.run(
        command, capture_output=True, text=True, check=False, cwd="/app"
    )


# Expected content snippets for assertions (to avoid too much repetition)
# These are based on the ReferenceLinkConverter's behavior.

expected_refs_end_content_snippet = """
<!-- REFERENCE LINKS -->
[alt-text-for-image]: images/my_image.png
[inline-link-to-google]: https://www.google.com
[link-to-openai]: https://www.openai.com
[link-to-pydantics-documentation]: https://docs.pydantic.dev/
<!-- END REFERENCE LINKS -->"""

# For section placement, the order might vary based on link discovery.
# We'll check for the presence of converted links and their definitions.

def normalize_whitespace(text: str) -> str:
    """Normalizes whitespace in a string for comparison."""
    return "".join(text.split())


def test_cli_reflinks_to_new_file_placement_end(create_temp_md_file, tmp_path: Path):
    """Test CLI reflinks to a new file with 'end' placement."""
    input_filename = "input.md"
    output_filename = "output.md"
    input_md_path = create_temp_md_file(input_filename, sample_md_inline_links)
    output_md_path = tmp_path / output_filename

    result = run_markitect_cli([
        "links", "reflinks",
        f"--input={str(input_md_path)}",  # Using Pydantic-settings format
        f"--output={str(output_md_path)}",
        "--placement=end"
    ])

    assert result.returncode == 0, f"CLI Error: {result.stderr or result.stdout}"
    assert output_md_path.exists()

    output_content = output_md_path.read_text(encoding="utf-8")
    input_content_original = input_md_path.read_text(encoding="utf-8")

    assert sample_md_inline_links == input_content_original, "Input file should not be changed."

    # Check for converted links
    assert "[inline link to Google][inline-link-to-google]" in output_content
    assert "![alt text for image][alt-text-for-image]" in output_content
    # Check for reference definitions
    assert normalize_whitespace(expected_refs_end_content_snippet) in normalize_whitespace(output_content)


def test_cli_reflinks_inplace_placement_section(create_temp_md_file, tmp_path: Path):
    """Test CLI reflinks in-place with 'section' placement."""
    input_filename = "input_sections.md"
    input_md_path = create_temp_md_file(input_filename, sample_md_with_sections)
    original_content = input_md_path.read_text(encoding="utf-8") # Save for comparison if needed

    result = run_markitect_cli([
        "links", "reflinks",
        f"--input={str(input_md_path)}",
        "--placement=section"
    ])

    assert result.returncode == 0, f"CLI Error: {result.stderr or result.stdout}"

    modified_content = input_md_path.read_text(encoding="utf-8")
    assert original_content != modified_content, "Input file should have been modified."

    # Check for converted links
    assert "Some text with [an inline link][an-inline-link]." in modified_content
    assert "More text and [another link][another-link] for this section." in modified_content
    assert "Text for chapter 2, including a [third link][third-link]." in modified_content

    # Check for reference definitions within sections (simplified check)
    # The exact output for section placement is complex due to comments and separators.
    # We'll check that the definitions are present.
    # A more robust check would parse the markdown or use more specific regex.
    assert normalize_whitespace("[an-inline-link]: https://example.com/page1") in normalize_whitespace(modified_content)
    assert normalize_whitespace("[another-link]: https://example.com/page2") in normalize_whitespace(modified_content)
    assert normalize_whitespace("[third-link]: https://example.com/page3") in normalize_whitespace(modified_content)

    # Verify structure for one of the sections to ensure refs are not all at the end
    # This checks that page1 and page2 refs are not at the very end of the document.
    assert "<!-- AN INLINE LINK REFERENCE LINKS -->" in modified_content
    assert "<!-- ANOTHER LINK REFERENCE LINKS -->" in modified_content
    assert "<!-- THIRD LINK REFERENCE LINKS -->" in modified_content


def test_cli_reflinks_default_placement_inplace(create_temp_md_file, tmp_path: Path):
    """Test CLI reflinks in-place with default placement (should be 'end')."""
    input_filename = "input_default.md"
    input_md_path = create_temp_md_file(input_filename, sample_md_inline_links)
    original_content = input_md_path.read_text(encoding="utf-8")

    # Using input short alias 'i'
    result = run_markitect_cli(["links", "reflinks", f"-i{str(input_md_path)}"])

    assert result.returncode == 0, f"CLI Error: {result.stderr or result.stdout}"
    modified_content = input_md_path.read_text(encoding="utf-8")

    assert original_content != modified_content, "Input file should have been modified."
    assert "[inline link to Google][inline-link-to-google]" in modified_content
    assert "![alt text for image][alt-text-for-image]" in modified_content
    assert normalize_whitespace(expected_refs_end_content_snippet) in normalize_whitespace(modified_content)


def test_cli_reflinks_input_file_not_found():
    """Test CLI reflinks command with a non-existent input file."""
    non_existent_file = "non_existent_file.md"
    result = run_markitect_cli(["links", "reflinks", f"--input={non_existent_file}"])

    assert result.returncode != 0
    # Pydantic settings error message for FilePath type
    # The exact message can vary based on Pydantic version and OS
    # We check for key parts.
    expected_error_msg_part = f"Path \"{non_existent_file}\" does not exist"
    
    # Depending on how Typer/Pydantic reports this, it could be in stderr or stdout.
    # For pydantic-settings, validation errors often go to stdout with the help message.
    assert expected_error_msg_part in result.stdout or expected_error_msg_part in result.stderr, \
        f"Expected error message not found in CLI output.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

def test_cli_reflinks_no_input_file_provided():
    """Test CLI reflinks command when no input file is provided."""
    result = run_markitect_cli(["links", "reflinks"])

    assert result.returncode != 0
    # Pydantic settings will complain about a missing required field.
    # The message structure might be like: "input_file\n  Field required [type=missing..."
    # or "1 validation error for ReferenceLinksCommand\ninput_file\n  Field required"
    # For pydantic-settings with CLI parsing, missing required args usually print help.
    assert "input_file" in result.stdout or "input_file" in result.stderr
    assert "Field required" in result.stdout or "Field required" in result.stderr or "Missing argument" in result.stdout, \
        f"Expected error message not found in CLI output.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

# Add a test for --help to ensure the command is registered
def test_cli_reflinks_help():
    """Test that the 'links reflinks --help' command works."""
    result = run_markitect_cli(["links", "reflinks", "--help"])
    assert result.returncode == 0
    assert "Usage: python -m markitecture links reflinks" in result.stdout
    assert "Convert inline markdown links to reference-style links." in result.stdout
    assert "--input" in result.stdout
    assert "--output" in result.stdout
    assert "--placement" in result.stdout
    assert "Input File" in result.stdout # Check for one of the key-value table headers from the command itself
    assert "Output File" in result.stdout
    assert "Placement" in result.stdout

def test_cli_links_help():
    """Test that the 'links --help' command works and shows subcommands."""
    result = run_markitect_cli(["links", "--help"])
    assert result.returncode == 0
    assert "Usage: python -m markitecture links" in result.stdout
    assert "Manage and convert document links." in result.stdout # Description of LinksGroupCommand
    assert "check" in result.stdout # Subcommand
    assert "reflinks" in result.stdout # Subcommand
