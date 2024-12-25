"""Utilities for sanitizing filenames from markdown headers."""

import html
import re
from pathlib import Path


def sanitize_filename(text: str, extension: str = ".md") -> Path:
    """
    Convert a markdown header into a safe filename.

    This function handles complex markdown headers containing images, HTML entities,
    and special characters, converting them into clean, filesystem-safe filenames.

    Args:
        text: The header text to sanitize
        extension: File extension to append (defaults to .md)

    Returns:
        Path object with sanitized filename

    Example:
        >>> sanitize_filename('#### ![bash][bash-svg]{ width="2%" }&emsp13;Bash')
        Path('bash.md')
    """
    # First, decode any HTML entities
    text = html.unescape(text)

    # Remove markdown heading markers
    text = re.sub(r"^#+\s*", "", text)

    # Remove image references and other markdown links
    # Matches both ![alt][ref] and [text][ref] patterns
    text = re.sub(r"!\[([^\]]*)\]\[[^\]]*\]", r"\1", text)  # Image references
    text = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", text)  # Regular references

    # Remove markdown attributes in curly braces
    text = re.sub(r"\{[^}]*\}", "", text)

    # Remove any remaining markdown syntax
    text = re.sub(r"[*_`~]", "", text)

    # Handle special cases where image alt text is empty
    if not text.strip():
        # Try to extract reference name from image/link references
        ref_match = re.search(r"\]\[([^\]]+)\]", text)
        if ref_match:
            text = ref_match.group(1)

    # Convert to lowercase and replace spaces/special chars with hyphens
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)  # Remove any remaining special characters
    text = re.sub(r"[-\s]+", "-", text)  # Replace spaces and repeated hyphens

    # Remove leading/trailing hyphens
    text = text.strip("-")

    # Ensure we have valid text
    if not text:
        text = "unnamed-section"

    # Add extension and return as Path object
    return Path(f"{text}{extension}")


# Additional utility functions for special cases
def strip_markdown_header(text: str) -> str:
    """Remove only the markdown header markers from text.

    Args:
        text: The header text containing markdown syntax

    Returns:
        Text with header markers removed but other formatting intact
    """
    return re.sub(r"^#+\s*", "", text)


def extract_image_alt_text(text: str) -> str:
    """Extract alt text from markdown image references.

    Args:
        text: Text containing markdown image references

    Returns:
        Extracted alt text or empty string if none found
    """
    match = re.search(r"!\[([^\]]*)\]", text)
    return match.group(1) if match else ""
