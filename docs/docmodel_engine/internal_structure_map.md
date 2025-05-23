# Internal "Structure Map" (Phase 0, Deliverable 6)

## Reiterated Theme/Goal

The Internal "Structure Map" is a semantically richer, hierarchical representation of a Markdown document, built from the initial raw Abstract Syntax Tree (AST) provided by a standard Markdown parser. Its purpose is to provide a standardized, queryable, and enriched data structure that Markitect's various analysis, validation, and transformation features can operate on more effectively than directly using a raw, parser-specific AST. This map forms a foundational component for advanced features like documentation smell detection (FR6.2), content visualization (FR6.1), and complex cross-document consistency checks.

## Design Principles

1.  **Semantic Richness:** Capture not just the syntax (like a raw AST) but also the implied semantic roles of elements (e.g., this heading represents a "Section Title").
2.  **Standardization:** Provide a consistent internal representation regardless of the underlying Markdown parser used (e.g., `mistune`, `markdown-it-py`). This allows Markitect's core logic to be parser-agnostic.
3.  **Queryability:** Design the structure to be easily traversed and queried for specific elements or patterns (e.g., "find all level 2 headings," "get all code blocks with language 'python'").
4.  **Extensibility:** Allow for future enrichment with more metadata, analysis results, or new structural element types without breaking core functionality.
5.  **Traceability:** Maintain references to original AST nodes or source positions to allow mapping findings back to the original Markdown content for reporting and diagnostics.
6.  **Hierarchical Representation:** Reflect the nested nature of documents (sections containing subsections, lists containing items, etc.).

## Core Data Structures (Pydantic Models)

The following Pydantic models define the core components of the Document Structure Map.

```python
from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field as PydanticField
from uuid import UUID, uuid4 # For unique IDs
from pathlib import Path # For document path

# --- Forward Declarations & Type Aliases ---
# Allows recursive type definitions (e.g., children can be StructuralElement)
AnyStructuralElement = ForwardRef('AnyStructuralElement')


# --- Base and Common Elements ---

class SourceReference(BaseModel):
    """Reference to the original source or AST node."""
    # Option 1: Store raw AST node (can be complex, parser-specific)
    # raw_ast_node: Optional[Any] = None 
    # Option 2: Store line/column info (more standardized)
    start_line: int # 1-indexed
    start_column: Optional[int] = None # 1-indexed
    end_line: Optional[int] = None # 1-indexed
    end_column: Optional[int] = None # 1-indexed
    # raw_text_segment: Optional[str] = None # The raw text of the element

class BaseElement(BaseModel):
    """Base class for all structural elements."""
    id: UUID = PydanticField(default_factory=uuid4)
    element_type: str # e.g., "Heading", "Paragraph", "CodeBlock"
    source_ref: Optional[SourceReference] = None
    parent_id: Optional[UUID] = None # ID of the parent element
    # Markitect-specific metadata can be added here
    metadata: Dict[str, Any] = PydanticField(default_factory=dict)
    # Validation results specific to this element can be stored here
    # E.g., schema validation status, term check results for this element's content
    validation_issues: List[Any] = PydanticField(default_factory=list) # List of validation error objects

# --- Specific Structural Elements ---

class TextElement(BaseElement):
    """Represents a simple text run, often part of a Paragraph or Heading."""
    element_type: Literal["Text"] = "Text"
    content: str

class ParagraphElement(BaseElement):
    element_type: Literal["Paragraph"] = "Paragraph"
    # Content could be a list of mixed TextElement, LinkElement, ImageElement, etc. (inline content)
    # For Phase 0, might simplify to just raw text content of the paragraph.
    # For richer inline representation:
    # inline_content: List[Union[TextElement, LinkElement, ImageElement, 'EmphasisElement', 'StrongElement']]
    raw_text_content: str # The concatenated text content for simpler access

class HeadingElement(BaseElement):
    element_type: Literal["Heading"] = "Heading"
    level: int # e.g., 1 for H1, 2 for H2
    text: str # The textual content of the heading
    children: List[AnyStructuralElement] = PydanticField(default_factory=list) # Nested elements under this heading

class LinkElement(BaseElement):
    element_type: Literal["Link"] = "Link"
    text: str # The link text (e.g., "[link text](url)")
    destination: str # The URL or path
    link_type: Optional[Literal["internal_relative", "internal_absolute", "external", "email", "anchor"]] = None
    # Validation status from LinkChecker (Deliverable 3.1)
    validation_status: Optional[str] = None # e.g., "valid", "missing_file", "invalid_format"
    resolved_path: Optional[Path] = None # For internal links, the resolved absolute path

class ImageElement(BaseElement): # Similar to LinkElement
    element_type: Literal["Image"] = "Image"
    alt_text: str
    source_url: str
    title: Optional[str] = None

class CodeBlockElement(BaseElement):
    element_type: Literal["CodeBlock"] = "CodeBlock"
    language: Optional[str] = None # e.g., "python", "javascript"
    content: str
    # Syntax validation results from CodeSyntaxValidator (Deliverable 3.2)
    syntax_validation_errors: List[Any] = PydanticField(default_factory=list) # List of SyntaxErrorDetail objects

class ListItemElement(BaseElement):
    element_type: Literal["ListItem"] = "ListItem"
    # List items can contain paragraphs, nested lists, etc.
    # For Phase 0, might be simplified to raw text or a list of ParagraphElements.
    # For richer structure:
    # content_elements: List[Union[ParagraphElement, ListElement, CodeBlockElement]]
    raw_text_content: str # Concatenated text of the list item for simple cases
    # If list items can have nested structures:
    # children: List[AnyStructuralElement] = PydanticField(default_factory=list)


class ListElement(BaseElement): # Represents a complete list (ul or ol)
    element_type: Literal["List"] = "List"
    ordered: bool # True for ordered list (ol), False for unordered (ul)
    start_number: Optional[int] = None # For ordered lists, if not starting at 1
    items: List[ListItemElement] = PydanticField(default_factory=list)
    # Or, if list items can have complex nested structures directly:
    # items_structured: List[AnyStructuralElement] = PydanticField(default_factory=list)


class BlockQuoteElement(BaseElement):
    element_type: Literal["BlockQuote"] = "BlockQuote"
    # Content is typically a list of other block elements like Paragraphs
    children: List[AnyStructuralElement] = PydanticField(default_factory=list)

class ThematicBreakElement(BaseElement): # Horizontal Rule (---, ***)
    element_type: Literal["ThematicBreak"] = "ThematicBreak"

class FrontmatterElement(BaseElement): # For document metadata (e.g., YAML frontmatter)
    element_type: Literal["Frontmatter"] = "Frontmatter"
    data: Dict[str, Any] # Parsed frontmatter data

# --- Union Type for Any Structural Element ---
# This defines what can go into `children` lists.
AnyStructuralElement = Union[
    HeadingElement,
    ParagraphElement,
    CodeBlockElement,
    ListElement, # ListItemElement is typically contained within ListElement
    LinkElement, # Links are often inline, so might be part of Paragraph content
    ImageElement, # Similar to Links
    TextElement, # For inline content representation
    BlockQuoteElement,
    ThematicBreakElement,
    FrontmatterElement
    # Add other elements like TableElement, EmphasisElement, StrongElement as needed
]

# Update forward references for all models that use it.
HeadingElement.update_forward_refs(AnyStructuralElement=AnyStructuralElement)
BlockQuoteElement.update_forward_refs(AnyStructuralElement=AnyStructuralElement)
# If ListItemElement were to have complex children directly:
# ListItemElement.update_forward_refs(AnyStructuralElement=AnyStructuralElement)


# --- Root Document Structure ---

class DocumentStructure(BaseModel):
    """The root object representing the structured map of a single document."""
    doc_path: Path # Filesystem path of the document
    frontmatter: Optional[FrontmatterElement] = None
    elements: List[AnyStructuralElement] = PydanticField(default_factory=list) # Top-level elements
    metadata: Dict[str, Any] = PydanticField(default_factory=dict) # Document-level metadata
    # Global validation summary for the document
    # E.g., schema_id_applied, overall_schema_conformance_status
    doc_validation_summary: Dict[str, Any] = PydanticField(default_factory=dict)

```

## Construction Process Overview

The `DocumentStructure` is built by processing the raw AST generated by a Markdown parser (e.g., `markdown-it-py`, `mistune`, or `CommonMark-py`).

1.  **Initial Parsing:** The source Markdown document is first parsed by a chosen library into its raw AST. This AST is specific to the parser library.
2.  **AST Adaptation/Normalization (Optional but Recommended):**
    *   A thin adapter layer might be used to provide a slightly more consistent interface over different parsers' ASTs, or specific node types might be handled directly.
3.  **Recursive Traversal and Mapping:**
    *   A "Structure Builder" component traverses the raw AST nodes recursively.
    *   For each significant raw AST node type, it maps it to one of Markitect's `StructuralElement` Pydantic models.
        *   **Headings:** A raw heading node becomes a `HeadingElement`. Its level and text content are extracted. Subsequent AST nodes are processed as children of this `HeadingElement` until a heading of the same or higher level is encountered, thus forming the hierarchy.
        *   **Paragraphs:** Raw paragraph nodes become `ParagraphElement`s. Their inline content (text, links, images) is processed. For Phase 0, this might be simplified to extracting the raw text content.
        *   **Code Blocks:** Raw code block nodes become `CodeBlockElement`s, capturing language and content.
        *   **Lists:** Raw list nodes (and their item nodes) become `ListElement` and `ListItemElement`s. Nested lists are handled by recursively processing list items' children.
        *   **Links/Images:** Inline link/image nodes in the AST are mapped to `LinkElement`/`ImageElement`. These might be nested within the `raw_text_content` of a `ParagraphElement` or stored in a more structured `inline_content` list.
        *   **Frontmatter:** If the parser supports frontmatter (or a pre-processing step extracts it), it's mapped to `FrontmatterElement`.
    *   **Parent-Child Relationships:** As the AST is traversed, `parent_id` fields are set for child elements, and `children` lists are populated for container elements like `HeadingElement`.
    *   **Source References:** Line/column information from the raw AST nodes is crucial and stored in `SourceReference` for each `StructuralElement`.
    *   **Unique IDs:** Each `StructuralElement` is assigned a unique `id` (UUID).
4.  **Enrichment (Post-Traversal or During):**
    *   After the basic structure is built, or during its construction, Markitect can enrich it:
        *   **Link Classification & Validation:** `LinkElement.link_type` and `LinkElement.validation_status` can be populated by running the link checking logic (Deliverable 3.1).
        *   **Code Syntax Validation:** `CodeBlockElement.syntax_validation_errors` can be populated by the code syntax validator (Deliverable 3.2).
        *   **Schema Validation Metadata:** The `doc_validation_summary` in `DocumentStructure` or `validation_issues` in individual `BaseElement`s can be updated based on DocModel schema validation (Deliverable 1).

The output of this process is a single `DocumentStructure` instance for the parsed Markdown file, representing Markitect's understanding of that document.

## Key Information to Capture

For each `StructuralElement`, Markitect aims to capture:

*   **`id` (UUID):** A unique identifier for the element within the entire system (or at least within the document context if IDs are not globally unique).
*   **`element_type` (str):** The Markitect-defined type of the element (e.g., "Heading", "Paragraph").
*   **`parent_id` (Optional[UUID]):** The ID of the hierarchical parent, enabling reconstruction of the document tree.
*   **`source_ref` (SourceReference):** Line and column numbers from the original Markdown, allowing direct mapping of issues or features back to the source text. The raw text segment could also be stored here.
*   **Content:** The actual data of the element (text for headings/paragraphs, code for code blocks, items for lists, etc.).
*   **Hierarchy (`children`):** For container elements like `HeadingElement` or `ListElement`, a list of their child `StructuralElement`s.
*   **Markitect-Specific Metadata (`metadata` dict):** An extensible dictionary for storing information derived by Markitect's analysis (e.g., semantic role, quality scores, smell indicators - future).
*   **Validation Results (`validation_issues`, `syntax_validation_errors`, `link_type`, `validation_status`):** Results from various checks (schema, code syntax, link validity) are directly associated with the elements they pertain to.

## Distinction from Raw AST

While the raw AST from a parser is essential as the input, the `DocumentStructure` map offers several advantages for Markitect's internal operations:

1.  **Standardization:** It provides a consistent data model for Markitect's tools, irrespective of which underlying Markdown parser (e.g., `mistune`, `commonmark-py`, `markdown-it-py`) might be used or swapped out in the future. Markitect's core logic interacts with this standardized map.
2.  **Semantic Enrichment:** The map is not just a syntax tree. It's designed to capture higher-level semantic understanding. For example, a `HeadingElement` explicitly defines a section and contains its children, which is a more direct representation of document structure than navigating generic AST nodes.
3.  **Queryability and Ease of Use:** The Pydantic models with clearly defined fields and relationships are easier to query and manipulate in Python code compared to navigating potentially heterogeneous and less explicitly typed raw AST node structures. Finding "all level 2 headings" or "all Python code blocks" becomes a straightforward traversal and filtering of known types.
4.  **Integrated Metadata:** Markitect can directly attach its own metadata, analysis results (like validation statuses, smell indicators), and unique IDs to elements within this structure. Doing this on a raw AST might be more cumbersome or involve monkey-patching.
5.  **Reduced Complexity for Higher-Level Features:** Features like documentation smell detection (FR6.2) or content visualization (FR6.1) can operate on this well-defined, predictable structure, simplifying their implementation. They don't need to understand the intricacies of different raw AST formats.
6.  **State Management:** For LSP or interactive tools, this structure can hold the "current state" of the document as understood and validated by Markitect, including any transient issues.

## Application to Dynamic README Scenario

*   **`readme_maturity_levels.md` Representation:**
    *   The entire document would be a `DocumentStructure` instance.
    *   The main title (e.g., "Readme Maturity Levels") would be a `HeadingElement` (level 1) at the top of `DocumentStructure.elements`.
    *   Sections like "Introduction", "Bronze Level", "Silver Level", "Gold Level" would each be `HeadingElement`s (likely level 2), appearing as children of the root or a top-level section heading.
    *   Under each "Level X" `HeadingElement`, its description would be one or more `ParagraphElement`s.
    *   Characteristics or criteria for each level, often presented as bullet points, would be represented as a `ListElement` (with `ordered=False`). Each bullet point would be a `ListItemElement`, likely containing a `ParagraphElement` for its text.
    *   Any links (e.g., to examples or external standards) would be `LinkElement`s, potentially nested within paragraph or list item content, and would have their `link_type` and `validation_status` populated.
    *   If `readme_maturity_levels.md` itself is validated against a schema (e.g., a "FrameworkDefinitionDocument" archetype), the `doc_validation_summary` and individual element `validation_issues` would reflect this.

*   **`README.stub` Representation:**
    *   The `DocumentStructure` for `README.stub` would similarly map its headings, paragraphs, code blocks, etc.
    *   **Placeholders:**
        *   If placeholders like `<!-- TODO: Add project overview -->` or `[PROJECT_DESCRIPTION]` are used, they would initially be part of the `raw_text_content` of `ParagraphElement`s or other text-bearing elements.
        *   Markitect could, in a later phase or through specific schema rules, identify these placeholders and either:
            *   Store information about them in the `metadata` of the containing `StructuralElement`.
            *   Introduce a specific `PlaceholderElement` type if they need to be treated as distinct structural components with their own validation or processing logic. For Phase 0, they are likely just text.
    *   Code blocks (` ```python ... ``` `) would be `CodeBlockElement`s, and their `syntax_validation_errors` list would be populated if errors are found.
    *   Links to `CONTRIBUTING.md` or `LICENSE` would be `LinkElement`s with their status checked.

*   **Input to Validators:**
    *   The `DocumentStructure` serves as a common, enriched input for various validation and analysis stages.
    *   **Schema Validation (DocModel Engine):** Instead of the `ValidatorEngine` directly re-traversing a raw AST for every document, it could operate on this `DocumentStructure`. The schema rules (e.g., "expected element 'Introduction' of type Heading") would map to queries on the `DocumentStructure` (e.g., "find child of type `HeadingElement` with text 'Introduction'"). This can simplify the validator's traversal logic as it works with a more predictable and semantically annotated tree.
    *   **Consistency Checks (Terms, Links):** The `ConsistencyChecker` would iterate through `ParagraphElement.raw_text_content`, `HeadingElement.text`, etc., from the `DocumentStructure` to find terms. It would inspect `LinkElement`s directly.
    *   **Code Syntax Validation:** The `CodeValidationService` would operate on `CodeBlockElement`s extracted into the `DocumentStructure`.
    *   This means the initial raw AST parsing happens once to build the `DocumentStructure`. Subsequent validation steps consume this map, potentially enriching it further with their results. This avoids redundant parsing and provides a shared understanding of the document's structure.

## Future Implications

*   **FR6.1 (Visualization):** The hierarchical `DocumentStructure` with its explicit parent-child relationships and element types is an ideal input for generating visualizations of the document's layout, such as a tree view, a mind map, or a section outline.
*   **FR6.2 (Smell Detection):** "Documentation smells" (e.g., overly long paragraphs, too many top-level sections, missing link text, shallow heading structures) can be detected by querying and analyzing the properties and relationships of elements within the `DocumentStructure`. For example:
    *   `len(paragraph_element.raw_text_content)` for paragraph length.
    *   `len(heading_element.children)` to analyze section content.
    *   Counting `LinkElement`s where `text` is empty or generic.
*   **Advanced Analysis & Transformation:** This structure provides a robust foundation for more sophisticated content analysis (e.g., readability scores per paragraph, identifying passive voice) or even automated document transformations and refactoring in the future.

By creating this internal, semantically rich "Structure Map," Markitect lays a strong foundation for a wide range of current and future documentation intelligence features.Okay, I have created the new Markdown document for Phase 0, Deliverable 6.

It is saved as: `docs/docmodel_engine/internal_structure_map.md`

The document covers:
1.  **Reiterated Theme/Goal:** Explains the purpose of the Internal Structure Map as an enhanced, semantically richer representation of Markdown for easier querying and analysis.
2.  **Design Principles:** Outlines guiding principles such as semantic richness, standardization, queryability, extensibility, traceability, and hierarchical representation.
3.  **Core Data Structures (Pydantic Models):**
    *   Defined Pydantic models for `DocumentStructure`, `BaseElement`, `SourceReference`.
    *   Specific element models: `HeadingElement`, `ParagraphElement`, `TextElement`, `CodeBlockElement`, `LinkElement`, `ImageElement`, `ListElement`, `ListItemElement`, `BlockQuoteElement`, `ThematicBreakElement`, and `FrontmatterElement`.
    *   An `AnyStructuralElement` Union type for defining children lists and ensuring type safety.
    *   Forward references are used for recursive type definitions.
4.  **Construction Process Overview:** Briefly described how the `DocumentStructure` is built by traversing and mapping nodes from a raw Markdown AST, including establishing parent-child relationships and enriching with validation results.
5.  **Key Information to Capture:** Detailed what information (ID, type, parent, source reference, content, hierarchy, metadata, validation results) is stored for each element.
6.  **Distinction from Raw AST:** Clarified the benefits of the `DocumentStructure` (standardization, semantic enrichment, queryability, integrated metadata, reduced complexity for higher-level features, state management).
7.  **Application to Dynamic README Scenario:**
    *   Explained how `readme_maturity_levels.md` would be represented, highlighting key elements like headings for levels and lists for characteristics.
    *   Described the representation of `README.stub`, including how placeholders might be handled initially and how code/link elements are captured.
    *   Clarified that this structure serves as a common, enriched input for validators, potentially simplifying their logic and avoiding redundant parsing.
8.  **Future Implications (Briefly):** Touched upon how this map lays the groundwork for FR6.1 (Visualization) and FR6.2 (Smell Detection) and other advanced analyses.

The Pydantic models are detailed, and the conceptual mapping from a raw AST to these models is explained, aligning with the requirements of the task.
