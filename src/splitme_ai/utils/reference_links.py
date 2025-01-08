"""Handles extraction and management of reference-style links in Markdown."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

from splitme_ai.logger import Logger

_logger = Logger(__name__)


class ReferenceHandler:
    """
    Handles extraction and management of reference-style links in Markdown.

    This class provides functionality to extract reference-style links from markdown
    content and track which references are actually used within specific sections.
    """

    def __init__(self, markdown_text: str) -> None:
        """
        Initialize the ReferenceHandler with the entire markdown content.

        Args:
            markdown_text: The full markdown content as a string.
        """
        self.markdown_text = markdown_text
        self.references = self._extract_references()

    def _extract_references(self) -> dict[str, str]:
        """
        Extract reference-style links from the markdown text.

        A reference link follows the pattern:
        [refname]: http://example.com

        Returns:
            Dictionary mapping reference names to their URLs.
        """
        # Extract references that appear after reference marker comments
        ref_sections = re.split(r"<!--\s*REFERENCE\s+LINKS\s*-->", self.markdown_text)

        references = {}
        ref_pattern = re.compile(r"^\[([^\]]+)\]:\s*(.+?)\s*$", re.MULTILINE)

        # Process each reference section (if any exist)
        for section in ref_sections:
            for match in ref_pattern.finditer(section):
                ref_name = match.group(1).strip()
                ref_link = match.group(2).strip()
                references[ref_name] = ref_link

        return references

    def find_used_references(self, section_content: str) -> dict[str, str]:
        """
        Find which references are actually used within a given section.

        A reference is considered used if it appears in the form [refname]
        within the section content, excluding the reference definitions themselves.

        Args:
            section_content: The markdown content of a section to analyze.

        Returns:
            Dictionary of references that are actually used in the section,
            mapping reference names to their URLs.
        """
        used_refs: Dict[str, str] = {}

        # Remove any existing reference definitions from the content
        content_without_refs = re.sub(
            r"\n*<!--\s*REFERENCE\s+LINKS\s*-->\n*.*$",
            "",
            section_content,
            flags=re.DOTALL,
        )

        # Find all reference usages, excluding image or link definitions
        ref_usage_pattern = re.compile(r"\[([^\]]+)\](?!\(|\:)")
        found = ref_usage_pattern.findall(content_without_refs)

        # Only include references that exist and are actually used
        for ref in found:
            if ref in self.references:
                used_refs[ref] = self.references[ref]

        return used_refs


class ReflinkConverter:
    """Converts inline Markdown links to reference-style links."""

    def __init__(self) -> None:
        """Regex for finding Markdown links, including image links."""
        self.link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"

    def extract_links(self, content: str) -> List[Tuple[str, str, str]]:
        """
        Extract all markdown links from the content.

        Args:
            content: The markdown content to process

        Returns:
            List of tuples: (original_text, text, url)
        """
        matches = re.finditer(self.link_pattern, content)
        return [(match.group(0), match.group(1), match.group(2)) for match in matches]

    def generate_reference_id(self, text: str, used_refs: Dict[str, str]) -> str:
        """
        Generate a unique reference ID based on the link text.

        Args:
            text: The link text to generate an ID for
            used_refs: Dictionary of already used reference IDs

        Returns:
            A unique reference ID
        """
        # Remove any leading ! for image links
        text = text.lstrip("!")

        # Create a basic reference from the text
        ref = re.sub(r"[^\w\s-]", "", text.lower())
        ref = re.sub(r"[-\s]+", "-", ref).strip("-")

        if not ref:
            ref = "link"

        # Handle duplicates
        base_ref = ref
        counter = 1
        while ref in used_refs and used_refs[ref] != text:
            ref = f"{base_ref}-{counter}"
            counter += 1

        return ref

    def convert_to_reflinks(self, content: str) -> str:
        """
        Convert all regular Markdown links to reference-style links.

        Args:
            content: The markdown content to process

        Returns:
            Modified content with reference-style links
        """
        links = self.extract_links(content)
        if not links:
            return content

        references = {}
        used_refs = {}
        modified_content = content

        reference_section = "\n\n---\n\n<!-- REFERENCE LINKS -->\n"

        for original, text, url in links:
            ref_id = self.generate_reference_id(text, used_refs)
            used_refs[ref_id] = text
            references[ref_id] = url

            is_image = text.startswith("!")
            ref_link = f"![{text[1:]}][{ref_id}]" if is_image else f"[{text}][{ref_id}]"

            modified_content = modified_content.replace(original, ref_link)
            reference_section += f"[{ref_id}]: {url}\n"

        return modified_content.rstrip() + reference_section

    def process_content(self, content: str) -> str:
        """
        Process markdown content directly and return the modified content.

        Args:
            content: The markdown content to process

        Returns:
            Processed content with reference-style links
        """
        return self.convert_to_reflinks(content)

    def process_file(
        self, input_path: str | Path, output_path: str | Path | None = None
    ) -> None:
        """
        Process a markdown file and save to a new file.

        Args:
            input_path: Path to the input markdown file
            output_path: Path to save the output file (optional)

        Raises:
            FileNotFoundError: If input file doesn't exist
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        content = input_path.read_text(encoding="utf-8")
        modified_content = self.convert_to_reflinks(content)

        output_path = Path(output_path) if output_path else input_path
        output_path.write_text(modified_content, encoding="utf-8")
