"""Module for sanitizing markdown headers into safe filenames."""

import html
import re
from pathlib import Path


def sanitize_filename(text: str, extension: str = ".md") -> Path:
    """
    Convert a markdown header into a safe filename.

    Args:
        text: The header text to sanitize
        extension: File extension to append (defaults to .md)

    Returns:
        Path object with sanitized filename
    """
    # Decode HTML entities
    text = html.unescape(text)

    # Remove markdown heading markers
    text = re.sub(r"^#+\s*", "", text)

    # Remove image references and other markdown links
    text = re.sub(r"!\[([^\]]*)\]\[[^\]]*\]", r"\1", text)  # Image references
    text = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", text)  # Regular references

    # Remove HTML tags and attributes (inline HTML)
    text = re.sub(r"<[^>]+>", "", text)

    # Remove markdown attributes in curly braces (e.g., {#custom-id}, {#})
    text = re.sub(r"\{[^}]*\}", "", text)

    # Remove any remaining markdown syntax
    text = re.sub(r"[*_`~]", "", text)

    # Handle special cases where text is empty
    if not text.strip():
        text = "unnamed-section"

    # Convert to lowercase and replace spaces/special chars with hyphens
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)  # Remove special characters
    text = re.sub(r"[-\s]+", "-", text)  # Replace spaces and repeated hyphens

    # Remove leading/trailing hyphens
    text = text.strip("-")

    if not text:
        text = "unnamed-section"

    return Path(f"{text}{extension}")


def extract_image_alt_text(text: str) -> str:
    """Extract alt text from markdown image references.

    Args:
        text: Text containing markdown image references

    Returns:
        Extracted alt text or empty string if none found
    """
    match = re.search(r"!\[([^\]]*)\]", text)
    return match.group(1) if match else ""


def strip_markdown_header(text: str) -> str:
    """Remove only the markdown header markers from text.

    Args:
        text: The header text containing markdown syntax

    Returns:
        Text with header markers removed but other formatting intact
    """
    return re.sub(r"^#+\s*", "", text)
