"""Core functionalities for markdown text splitting and processing."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from splitme_ai.cli import SplitmeApp, SplitmeSettings
from splitme_ai.logger import Logger
from splitme_ai.tools.reference_link_extractor import ReferenceLinkExtractor
from splitme_ai.utils.filename_sanitizer import sanitize_filename

_logger = Logger(__name__)


@dataclass
class Section:
    """
    Represents a split markdown section.
    """

    title: str
    content: str
    level: int
    filename: Path
    parent_context: str | None = None
    references: dict[str, str] | None = None

    def __post_init__(self) -> None:
        if self.references is None:
            self.references = {}


class MarkdownSplitter:
    """Splits markdown documents based on headings."""

    def __init__(self, settings: Optional[SplitmeSettings] = None) -> None:
        self.settings = settings or SplitmeSettings()
        self._compile_patterns()
        _logger.debug(f"Initialized MarkdownSplitter with settings: {self.settings}")

    def process_file(self, content: str) -> List[Section]:
        """Process markdown file, split it, and handle additional steps."""
        _logger.info("Starting markdown file processing")
        sections = self.split(content)

        _logger.debug(f"Creating output directory: {self.settings.output_dir}")
        self.settings.output_dir.mkdir(parents=True, exist_ok=True)

        for section in sections:
            section_path = self.settings.output_dir / section.filename
            _logger.debug(f"Writing section '{section.title}' to {section_path}")
            section_path.write_text(section.content, encoding="utf-8")

        if hasattr(self.settings, "process_mkdocs"):
            _logger.info("Mkdocs configuration enabled. Processing...")
            self.settings.process_mkdocs()

        _logger.info("File processing completed successfully")
        return sections

    def split(self, content: str) -> List[Section]:
        """
        Split markdown content into sections based on specified heading level.
        Respects heading hierarchy - only splits at specified level and includes
        appropriate nested content without including higher-level content.
        Properly handles code blocks and comments within headings.
        """
        _logger.info("Executing text splitting...")

        ref_handler = ReferenceLinkExtractor(content)

        _logger.debug(
            f"Extracted {len(ref_handler.references)} references from content"
        )

        # First, identify all code block positions to exclude them from heading search
        code_blocks = []

        # Match fenced code blocks (both ``` and ~~~)
        fenced_blocks = re.finditer(
            r"(?:```|~~~)[^\n]*\n.*?(?:```|~~~)", content, re.DOTALL
        )
        code_blocks.extend(fenced_blocks)

        # Match indented code blocks (4 spaces or 1 tab)
        lines = content.split("\n")
        i = 0
        while i < len(lines):
            if re.match(r"^(?:\s{4}|\t).*$", lines[i]):
                # Found start of indented block
                start_pos = len("\n".join(lines[:i]))
                # Find end of block
                while i < len(lines) and (
                    re.match(r"^(?:\s{4}|\t).*$", lines[i]) or lines[i].strip() == ""
                ):
                    i += 1
                end_pos = len("\n".join(lines[:i]))
                # Create a proper class instance for block matching

                class BlockMatch:
                    def __init__(self, start_pos, end_pos):
                        self._start = start_pos
                        self._end = end_pos

                    def start(self, *args):
                        return self._start

                    def end(self, *args):
                        return self._end

                code_blocks.append(BlockMatch(start_pos, end_pos))
            i += 1

        # Find all headings of any level (# through ######), excluding those in code blocks
        all_headings = []
        for match in re.finditer(
            r"^(#{1,6})\s+(.+?)(?:\s+<!--.*?-->)*\s*$", content, re.MULTILINE
        ):
            # Check if this heading is inside any code block
            is_in_code_block = any(
                block.start() <= match.start() <= block.end() for block in code_blocks
            )
            if not is_in_code_block:
                all_headings.append(match)

        headings = all_headings
        if not headings:
            _logger.info("No headings found. Creating single README section.")
            section = self._create_section(
                title="README",
                content=content,
                level=0,
                references=ref_handler.references,
            )
            return [section]

        # Target heading level is determined by number of # in settings
        target_level = len(self.settings.heading_level)
        sections = []

        # Track the current section being built
        current_section_start = None
        current_section_title = None

        for i, match in enumerate(headings):
            heading_level = len(match.group(1))  # Number of # symbols
            heading_title = match.group(2).strip()
            heading_start = match.start()

            # Determine where this heading's content ends
            next_heading_start = (
                headings[i + 1].start() if i < len(headings) - 1 else len(content)
            )

            if heading_level == target_level:
                # If we were building a previous section, finalize it
                if current_section_start is not None:
                    section_content = content[
                        current_section_start:heading_start
                    ].strip()
                    section_refs = ref_handler.find_used_references(section_content)

                    sections.append(
                        self._create_section(
                            title=current_section_title,
                            content=self._format_section_content(
                                section_content, section_refs
                            ),
                            level=target_level,
                            references=section_refs,
                        )
                    )

                # Start a new section
                current_section_start = heading_start
                current_section_title = heading_title

            elif heading_level > target_level and current_section_start is not None:
                # This is nested content for the current section, do nothing
                continue
            elif heading_level < target_level:
                # This is a higher-level heading, ignore its content
                if current_section_start is not None:
                    section_content = content[
                        current_section_start:heading_start
                    ].strip()
                    section_refs = ref_handler.find_used_references(section_content)

                    sections.append(
                        self._create_section(
                            title=current_section_title,
                            content=self._format_section_content(
                                section_content, section_refs
                            ),
                            level=target_level,
                            references=section_refs,
                        )
                    )
                    current_section_start = None
                    current_section_title = None

        # Don't forget to handle the last section if we were building one
        if current_section_start is not None:
            section_content = content[current_section_start:].strip()
            section_refs = ref_handler.find_used_references(section_content)

            sections.append(
                self._create_section(
                    title=current_section_title,
                    content=self._format_section_content(section_content, section_refs),
                    level=target_level,
                    references=section_refs,
                )
            )

        _logger.info(f"Successfully split content into {len(sections)} sections.")
        return sections

    def _compile_patterns(self) -> None:
        """Compile regex patterns based on settings."""
        flags = 0 if self.settings.case_sensitive else re.IGNORECASE

        # Patterns for parsing
        self.heading_pattern = re.compile(
            f"^({re.escape(self.settings.heading_level)})\\s+(.+?)(?:\\s+<!--.*?-->)*\\s*$",
            re.MULTILINE | flags,
        )

        self.reference_pattern = re.compile(r"^\[([^\]]+)\]:\s+(.+)$", re.MULTILINE)
        self.reference_usage = re.compile(r"\[([^\]]+)\](?!\()", re.MULTILINE)

    def _create_section(
        self, title: str, content: str, level: int, references: Dict[str, str]
    ) -> Section:
        """Create a new Section object."""
        _logger.debug(f"Creating section with title: {title}, level: {level}")
        return Section(
            title=title,
            content=content,
            level=level,
            filename=sanitize_filename(text=title),
            references=references,
        )

    def _format_section_content(self, content: str, references: Dict[str, str]) -> str:
        """
        Format section content with references and ensure proper spacing.

        Args:
            content: The main content of the section
            references: Dictionary of reference names to their URLs that are
                    actually used in this section

        Returns:
            Formatted content with thematic break, references, and proper spacing
        """
        if not content:
            return ""

        # Prepare the base content by trimming trailing whitespace
        base_content = content.rstrip()

        # Check if content already ends with a thematic break
        hr_pattern = re.compile(r"\n[*_-]{3,}\s*$")

        # Add thematic break if one doesn't exist
        if not hr_pattern.search(base_content):
            base_content += "\n\n---"

        # Only add references if there are any used in this section
        if references:
            ref_text = "\n\n<!-- REFERENCE LINKS -->\n"
            for ref_name, ref_url in sorted(references.items()):
                ref_text += f"[{ref_name}]: {ref_url}\n"
            base_content += ref_text

        # Ensure the file ends with exactly one newline
        return base_content.rstrip() + "\n"


def main():
    """CLI entry point for splitme-ai."""
    app = SplitmeApp()
    app.cli_cmd()


if __name__ == "__main__":
    main()
