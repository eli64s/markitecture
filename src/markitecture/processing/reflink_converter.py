"""Reference link handling with sectional placement support."""

import re
from dataclasses import dataclass
from enum import StrEnum, auto
from pathlib import Path
from typing import Dict, List, Optional


class ReferencePlacement(StrEnum):
    """Controls where reference links are placed in the document."""

    END = auto()
    SECTION = auto()


@dataclass
class Section:
    """Represents a markdown section with its references."""

    content: str
    level: int
    references: Dict[str, str]
    start: int
    end: int


class ReferenceLinkConverter:
    """converter for managing reference-style links with section support."""

    def __init__(self) -> None:
        """Initialize patterns for finding links and headers."""
        self.link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
        self.header_pattern = r"^(#{1,6})\s+(.+?)(?:\s+<!--.*?-->)*\s*$"

    def _extract_sections(self, content: str) -> List[Section]:
        """Extract document sections based on headers."""
        sections: List[Section] = []
        lines = content.splitlines()
        current_section: Optional[Section] = None

        for i, line in enumerate(lines):
            header_match = re.match(self.header_pattern, line)

            if header_match:
                # If we have a previous section, finalize it
                if current_section:
                    current_section.end = i
                    sections.append(current_section)

                # Start new section
                level = len(header_match.group(1))
                current_section = Section(
                    content="", level=level, references={}, start=i, end=-1
                )

        # Handle the last section
        if current_section:
            current_section.end = len(lines)
            sections.append(current_section)

        # If no sections found, treat entire document as one section
        if not sections:
            sections = [
                Section(
                    content=content, level=0, references={}, start=0, end=len(lines)
                )
            ]

        return sections

    def _process_section_content(
        self, content: str, section: Section, used_refs: Dict[str, str]
    ) -> str:
        """Process content for a single section, adding references if needed."""
        lines = content.splitlines()
        section_lines = lines[section.start : section.end]

        # Find all link matches in this section
        matches = list(re.finditer(self.link_pattern, "\n".join(section_lines)))
        if not matches:
            return content

        # Convert links and track references for this section
        modified_lines = section_lines.copy()
        references = {}

        for match in matches:
            original = match.group(0)
            text = match.group(1)
            url = match.group(2)

            # Generate reference ID
            ref_id = self._generate_reference_id(text, used_refs)
            used_refs[ref_id] = text
            references[ref_id] = url

            # Create reference style link
            is_image = text.startswith("!")
            ref_link = f"![{text[1:]}][{ref_id}]" if is_image else f"[{text}][{ref_id}]"

            # Replace in content
            for i, line in enumerate(modified_lines):
                if original in line:
                    modified_lines[i] = line.replace(original, ref_link)

        # Store references for this section
        section.references = references

        # Update content with modified lines
        lines[section.start : section.end] = modified_lines
        return "\n".join(lines)

    def _generate_reference_id(self, text: str, used_refs: Dict[str, str]) -> str:
        """Generate a unique reference ID based on the link text."""
        text = text.lstrip("!")
        ref = re.sub(r"[^\w\s-]", "", text.lower())
        ref = re.sub(r"[-\s]+", "-", ref).strip("-")

        if not ref:
            ref = "link"

        base_ref = ref
        counter = 1
        while ref in used_refs and used_refs[ref] != text:
            ref = f"{base_ref}-{counter}"
            counter += 1

        return ref

    def convert_to_reflinks(
        self, content: str, placement: ReferencePlacement = ReferencePlacement.END
    ) -> str:
        """Convert inline links to reference style with configurable placement."""
        sections = self._extract_sections(content)
        used_refs: Dict[str, str] = {}
        processed_content = content

        # Process each section
        for section in sections:
            processed_content = self._process_section_content(
                processed_content, section, used_refs
            )

        # Add references based on placement preference
        if placement == ReferencePlacement.END:
            # Add all references at end of document
            all_refs = {}
            for section in sections:
                all_refs.update(section.references)

            if all_refs:
                ref_section = "\n\n---\n\n<!-- REFERENCE LINKS -->\n"
                for ref_id, url in sorted(all_refs.items()):
                    ref_section += f"[{ref_id}]: {url}\n"
                processed_content = processed_content.rstrip() + ref_section + "\n"

        else:  # ReferencePlacement.SECTION
            # Add references at the end of each section
            lines = processed_content.splitlines()

            for section in reversed(
                sections
            ):  # Process in reverse to maintain positions
                reflink_comment = "REFERENCE LINKS"
                header_match = re.match(self.header_pattern, lines[section.start])
                if header_match:
                    reflink_comment = (
                        f"{header_match.group(2).upper()} {reflink_comment}"
                    )
                if section.references:
                    ref_text = f"<!-- {reflink_comment} -->\n"
                    for ref_id, url in sorted(section.references.items()):
                        ref_text += f"[{ref_id}]: {url}\n"

                    # Insert references at section end
                    lines.insert(section.end, f"{ref_text}\n---\n")

            processed_content = "\n".join(lines)

        return processed_content

    def process_file(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        placement: ReferencePlacement = ReferencePlacement.END,
    ) -> None:
        """Process a markdown file and save to a new file."""
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        content = input_path.read_text(encoding="utf-8")
        modified_content = self.convert_to_reflinks(content, placement)

        output_path = Path(output_path) if output_path else input_path
        output_path.write_text(modified_content, encoding="utf-8")
