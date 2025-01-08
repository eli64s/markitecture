"""Extract and manage reference-style links in Markdown content."""

from __future__ import annotations

import re
from typing import Dict

from splitme_ai.logger import Logger

_logger = Logger(__name__)


class ReferenceLinkExtractor:
    """
    Handles extraction and management of reference-style links in Markdown.

    This class provides functionality to extract reference-style links from markdown
    content and track which references are actually used within specific sections.
    """

    def __init__(self, markdown_text: str) -> None:
        """
        Initialize the ReferenceLinkExtractor with the entire markdown content.

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
