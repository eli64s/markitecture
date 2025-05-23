# Basic Context-Awareness: Cross-Document Consistency (Phase 0, Deliverable 3.1)

## Reiterated Theme/Goal

The primary goal of this feature (FR2.1) is to enhance the quality and maintainability of documentation sets by introducing basic context-aware checks. This includes ensuring consistent terminology across documents and validating the existence of internal and external links. This deliverable focuses on the foundational aspects: identifying terms and links, and performing basic validation without complex semantic analysis or live external checks.

## Technical Implementation Approach

### Term Consistency

Term consistency ensures that specific keywords, product names, feature names, or abbreviations are used uniformly across a defined set of documents.

**1. Term Definition & Storage:**

*   **Identification:** Terms will be defined in one or more "glossary" files (YAML or JSON format) and/or directly within the `markitect.yaml` configuration.
*   **Storage:** A `TermBank` class will load and manage these defined terms. Each term definition includes:
    *   `canonical_form`: The preferred way the term should be written (e.g., "DocModel Engine").
    *   `approved_alternatives`: A list of acceptable variations (e.g., ["DocModel", "document model engine"]).
    *   `case_sensitive`: A boolean flag (configurable per term, with a global default) indicating if matching should be case-sensitive.
    *   `description`: Optional explanation of the term.

*   **Pydantic Models for Term Definition:**

    ```python
    from typing import List, Optional, Dict
    from pydantic import BaseModel, Field as PydanticField

    class TermDefinition(BaseModel):
        canonical_form: str
        approved_alternatives: List[str] = PydanticField(default_factory=list)
        case_sensitive: Optional[bool] = None # If None, global default is used
        description: Optional[str] = None

    class GlossaryFileContent(BaseModel):
        # Glossary files map a term slug/ID to its definition
        terms: Dict[str, TermDefinition]
    ```

**2. Term Extraction from Documents:**

*   A `ConsistencyChecker` module will traverse the Markdown AST of each document.
*   Text content is extracted from relevant AST nodes (Paragraphs, Headings, ListItems, TableCells, etc.).
*   The `TermBank` will provide a mechanism (e.g., compiled regexes) to find occurrences of all defined term variants (canonical and approved alternatives) in the extracted text, respecting term boundaries (e.g., whole-word matching).

**3. Consistency Checking Logic:**

*   For each segment of text identified by the `TermBank` as matching a defined term variant:
    *   The match is checked against the term's `canonical_form` and `approved_alternatives`, respecting the effective `case_sensitive` setting.
    *   **Phase 0 Goal:** Ensure only approved forms (canonical or listed alternatives) are used.
    *   If `enforce_canonical_form` is `true` (a stricter, configurable option, default `false` for Phase 0):
        *   If the matched text is an `approved_alternative` but not identical to the `canonical_form` (considering case sensitivity), it's flagged as an error.
    *   If `enforce_canonical_form` is `false`:
        *   Any match to a `canonical_form` or an `approved_alternative` is considered valid.
    *   **Finding Unapproved Variations:** The primary challenge is identifying text that *should* be a defined term but is an *unapproved* variation (e.g., misspelling, wrong casing if sensitive, entirely different wording).
        *   For Phase 0, this might be limited. If a piece of text is found by a general search for the canonical form (e.g., case-insensitive search for "docmodel engine") but the exact text found does not match any approved variant (canonical or alternative, respecting their specific case sensitivity), it's an error. This is simpler than full fuzzy matching.
*   **Error Reporting:** Inconsistencies are reported with document path, location (line/column if available), the problematic text, and the suggested canonical form.

### Link Checking

Verifies internal links point to existing files and external links have a valid format.

**1. Link Extraction:**

*   The AST is traversed to find link nodes (e.g., type `link` in `mistune`).
*   Destination URL (href) and link text are extracted.

**2. File Existence Check (for Internal Links):**

*   **Identify Internal Links:** Links not starting with a known URL scheme (e.g., `http://`, `https://`).
    *   Links starting with `/` are relative to `project_root` (from `markitect.yaml`).
    *   Others (e.g., `../file.md`, `image.png`) are relative to the current document's directory.
*   **Resolve Path:** Paths are resolved to absolute file system paths.
*   **Check Existence:** The resolved path is checked using `Path.is_file()`.
*   **Anchor/Fragment Check:** For Phase 0, checking ` #anchor` validity within the target file is **out of scope**. `file.md#anchor` only checks for `file.md`.

**3. Basic URL Validation (for External Links):**

*   **Identify External Links:** Links starting with schemes like `http`, `https`.
*   **Format Check:** `urllib.parse.urlparse` checks for a valid structure (scheme and netloc).
*   **No HTTP Calls:** Phase 0 **does not** make live HTTP requests.

### Overall Workflow

1.  **Config Load:** `markitect.yaml` is loaded (specifies `project_root`, glossaries, term/link check settings, scopes).
2.  **Term Bank Init:** `TermBank` is populated.
3.  **File Discovery:** All Markdown files in scope are identified. A `Set[Path]` of all existing files in the project (or relevant subdirectories) is created for link checking.
4.  **AST Parsing:** Each scoped document is parsed into an AST (`ParsedDoc` object: filepath, AST, project_root).
5.  **Consistency Check:** For each `ParsedDoc`:
    *   `ConsistencyChecker` extracts text and uses `TermBank` to find term errors.
    *   `ConsistencyChecker` extracts links, resolves internal ones, checks existence against the project file set, and validates external link formats.
6.  **Report Results:** Errors are aggregated and reported.

## Configuration (`markitect.yaml`)

```yaml
# markitect.yaml

project_name: "MyProjectDocs"
project_root: "." # Root for resolving absolute links like /docs/file.md and for include/exclude globs

consistency_checks:
  scope: # Defines which files are processed for consistency checks
    include: # Globs are relative to project_root
      - "docs/**/*.md"
      - "*.md" # Include MD files in the project_root directory
    exclude:
      - "docs/archive/"
      - "**/draft_*.md"
      - "node_modules/"

  term_consistency:
    enabled: true
    default_case_sensitive: false # Global default for terms
    enforce_canonical_form: false # If true, flags approved_alternatives if not canonical
    glossaries: # List of paths to glossary files, relative to project_root
      - "docs/project-glossary.yaml"
    
    defined_terms: # Inline term definitions. Key is a unique slug/ID for the term entry.
      "k8s-term": # Slug for the term "Kubernetes"
        canonical_form: "Kubernetes"
        approved_alternatives: ["K8s"]
        # case_sensitive: true # Optional: if not set, uses default_case_sensitive
      "js-term":
        canonical_form: "JavaScript"
        approved_alternatives: ["JS"]
      "docmodel-engine-term":
        canonical_form: "DocModel Engine"
        approved_alternatives: ["DocModel"]
        case_sensitive: true # Overrides default_case_sensitive for this term

  link_checking:
    enabled: true
    # Future options:
    # allowed_external_schemes: ["http", "https", "mailto"]
    # ignore_anchor_errors: true # If anchor validation is added later

# --- Example docs/project-glossary.yaml ---
# terms: # Top-level key must be "terms"
#   "api-def": # Slug for this term entry
#     canonical_form: "Application Programming Interface"
#     approved_alternatives: ["API"]
#     case_sensitive: true # "API" is case-sensitive
#     description: "A set of rules allowing different software entities to communicate."
#   "cli-tool":
#     canonical_form: "Command-Line Interface"
#     approved_alternatives: ["CLI", "command line interface"]
#     # description: "A text-based interface for interacting with software."
```

## Application to Dynamic README Scenario

*   **Term Consistency:**
    *   **Defining Terms:** Terms from `readme_maturity_levels.md` (e.g., "Bronze Level," "Code Coverage") are defined in `project-glossary.yaml` or `markitect.yaml`.
        ```yaml
        # In docs/project-glossary.yaml (under 'terms:')
        # "maturity-bronze":
        #   canonical_form: "Bronze Level"
        #   case_sensitive: true
        # "code-cov":
        #   canonical_form: "Code Coverage"
        #   approved_alternatives: ["coverage"]
        ```
    *   **Scope:** `scope` in `markitect.yaml` includes `readme_maturity_levels.md` and `README.md` (or its source).
    *   **Enforcement:** If `README.md` uses "bronze lvl" or "code coverage report" (and "coverage report" is not an approved alternative), Markitect flags these.

*   **Link Checking:**
    *   **Links in `readme_maturity_levels.md`:**
        *   External: `[Contributor Covenant](https://www.contributor-covenant.org/)` -> format check.
        *   Internal: `[Coding Standards](/docs/internal/coding_standards.md)` -> resolves to `project_root/docs/internal/coding_standards.md`, checks existence.
    *   **Links in `README.md`:**
        *   `[Contributing](CONTRIBUTING.md)` -> checks for `CONTRIBUTING.md` in README's directory.
        *   `[License](LICENSE.txt)` -> checks for `LICENSE.txt`.
        *   `[Full Docs](/docs/index.md)` -> checks for `project_root/docs/index.md`.

## Core Function Signatures / Class Definitions (Conceptual)

```python
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, Optional
from urllib.parse import urlparse
import re
from pydantic import BaseModel, Field as PydanticField # Re-aliasing Field

# Pydantic models for TermDefinition, GlossaryFileContent, and Config as defined earlier

class ParsedDoc:
    filepath: Path
    ast: Any # e.g., list of tokens from mistune
    project_root: Path

    def __init__(self, filepath: Path, ast: Any, project_root: Path):
        self.filepath = filepath.resolve()
        self.ast = ast
        self.project_root = project_root.resolve()

class TermConsistencyError(BaseModel):
    doc_path: Path
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    problematic_text: str
    matched_term_variant: Optional[str] = None # Which known variant (if any) was matched by the raw text
    expected_canonical_form: str
    message: str

class LinkError(BaseModel):
    doc_path: Path
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    link_destination: str
    link_text: Optional[str] = None
    message: str

class TermBank:
    def __init__(self, term_definitions_map: Dict[str, TermDefinition], global_default_case_sensitive: bool, global_enforce_canonical_form: bool):
        self.terms_map = term_definitions_map # slug -> TermDefinition
        self.global_default_case_sensitive = global_default_case_sensitive
        self.global_enforce_canonical_form = global_enforce_canonical_form
        self._compiled_terms: List[Tuple[re.Pattern, TermDefinition, str, bool]] = [] # pattern, term_def, variant_str, is_canonical
        self._build_lookup()

    def _build_lookup(self):
        for term_slug, term_def in self.terms_map.items():
            effective_case_sensitive = term_def.case_sensitive if term_def.case_sensitive is not None else self.global_default_case_sensitive
            regex_flags = 0 if effective_case_sensitive else re.IGNORECASE
            
            variants_to_compile = [(term_def.canonical_form, True)] + [(alt, False) for alt in term_def.approved_alternatives]

            for variant_str, is_canonical_variant in variants_to_compile:
                if not variant_str: continue # Skip empty variants
                # Term boundary: \b might not be ideal for multi-word terms or terms with special chars.
                # Using a simplified word boundary for now. More complex regex might be needed.
                pattern_str = r'\b' + re.escape(variant_str) + r'\b'
                try:
                    compiled_pattern = re.compile(pattern_str, flags=regex_flags)
                    self._compiled_terms.append((compiled_pattern, term_def, variant_str, is_canonical_variant))
                except re.error as e:
                    print(f"Warning: Could not compile regex for term variant '{variant_str}' (slug: {term_slug}): {e}")
    
    def find_term_occurrences(self, text_block: str) -> List[Dict[str, Any]]:
        """Finds all occurrences of defined terms in text."""
        occurrences = []
        for pattern, term_def, variant_str, is_canonical_variant in self._compiled_terms:
            for match in pattern.finditer(text_block):
                occurrences.append({
                    "match_obj": match,
                    "term_definition": term_def,
                    "matched_variant_str": variant_str, # The specific variant string that matched
                    "is_canonical_variant": is_canonical_variant, # Was this the canonical string for the term?
                    "effective_case_sensitive": pattern.flags == 0 # Approximates if this match was case-sensitive
                })
        # Sort occurrences by start index to process them in order
        occurrences.sort(key=lambda x: x["match_obj"].start())
        return occurrences

class ConsistencyChecker:
    def __init__(self, project_root: Path, config_data: Dict[str, Any]): # config_data is parsed markitect.yaml
        self.project_root = project_root.resolve()
        self.config = config_data.get('consistency_checks', {})
        self.term_bank: Optional[TermBank] = None
        
        term_config = self.config.get('term_consistency', {})
        if term_config.get('enabled', False):
            loaded_term_defs: Dict[str, TermDefinition] = {}
            # Load from glossaries
            for glossary_path_str in term_config.get('glossaries', []):
                glossary_path = (self.project_root / glossary_path_str).resolve()
                if glossary_path.is_file():
                    # Assuming YAML for now
                    import yaml # Ensure PyYAML is a dependency
                    try:
                        with open(glossary_path, 'r', encoding='utf-8') as f:
                            content = yaml.safe_load(f)
                            glossary_content = GlossaryFileContent.parse_obj(content)
                            for slug, term_def_data in glossary_content.terms.items():
                                if slug not in loaded_term_defs: # Avoid duplicates, first wins or log warning
                                    loaded_term_defs[slug] = term_def_data
                                else:
                                    print(f"Warning: Duplicate term slug '{slug}' found in {glossary_path}. Keeping first definition.")
                    except Exception as e:
                        print(f"Error loading glossary {glossary_path}: {e}")
            # Load inline definitions (overwrites glossary if same slug)
            for slug, term_def_data in term_config.get('defined_terms', {}).items():
                 loaded_term_defs[slug] = TermDefinition.parse_obj(term_def_data) if isinstance(term_def_data, dict) else term_def_data


            self.term_bank = TermBank(
                loaded_term_defs,
                term_config.get('default_case_sensitive', False),
                term_config.get('enforce_canonical_form', False)
            )
        self.link_config = self.config.get('link_checking', {})

    def _get_text_nodes_from_ast(self, ast_nodes: List[Any]) -> List[Tuple[str, Optional[int]]]: # Text, LineNumber
        """Extracts text content from AST nodes along with approximate line numbers."""
        # This is highly dependent on the AST structure (e.g., mistune, commonmark-py)
        # For mistune v2/v3, iterate tokens, if token['type'] == 'text', get 'raw'.
        # Line numbers might be in token.get('props', {}).get('line_start') or similar.
        # This function needs to be implemented based on the chosen Markdown parser.
        # Placeholder:
        text_and_lines = []
        def_visitor(node, current_list):
            if isinstance(node, dict):
                line_num = node.get('props', {}).get('line_number', node.get('props', {}).get('line_start'))

                if node.get('type') == 'text': # Example for mistune-like
                    current_list.append((node.get('raw', ''), line_num))
                elif 'children' in node:
                    for child in node['children']:
                        def_visitor(child, current_list)
        for root_node in ast_nodes:
            def_visitor(root_node, text_and_lines)
        return text_and_lines


    def check_term_consistency_in_doc(self, doc: ParsedDoc) -> List[TermConsistencyError]:
        errors: List[TermConsistencyError] = []
        if not self.term_bank or not self.config.get('term_consistency', {}).get('enabled', False):
            return errors

        text_nodes = self._get_text_nodes_from_ast(doc.ast) # Get all text nodes with line info
        for text_content, line_num in text_nodes:
            if not text_content.strip(): continue

            occurrences = self.term_bank.find_term_occurrences(text_content)
            for occ in occurrences:
                match:re.Match = occ['match_obj']
                term_def:TermDefinition = occ['term_definition']
                matched_variant:str = occ['matched_variant_str']
                is_canonical_variant_match:bool = occ['is_canonical_variant']

                # Check if enforce_canonical_form is active for this term_bank or term_def
                enforce_canon = self.term_bank.global_enforce_canonical_form # Could be overridden per term_def in future

                if enforce_canon and not is_canonical_variant_match:
                    errors.append(TermConsistencyError(
                        doc_path=doc.filepath, line_number=line_num, column_number=match.start() + 1, # Approx column
                        problematic_text=match.group(0),
                        matched_term_variant=matched_variant,
                        expected_canonical_form=term_def.canonical_form,
                        message=f"Term '{match.group(0)}' is an approved alternative but not the canonical form '{term_def.canonical_form}'. (Canonical form enforced)"
                    ))
                # Phase 0 does not actively find *unapproved* variations unless find_term_occurrences is made much smarter.
                # The current find_term_occurrences only finds *approved* ones.
                # To find unapproved ones, one might iterate all words, and if a word is "close" to a canonical form
                # but not in its approved list, then it's an error. This is more complex (e.g., Levenshtein distance).
        return errors

    def _get_link_nodes_from_ast(self, ast_nodes: List[Any]) -> List[Dict[str, Any]]: # List of link node dicts
        """Extracts link nodes from AST. Highly parser-dependent."""
        # Placeholder - needs actual AST traversal.
        # For mistune, look for type 'link'.
        # Example for mistune v2/v3:
        link_nodes_data = []
        def visitor(node, current_list):
            if isinstance(node, dict):
                line_num = node.get('props', {}).get('line_number', node.get('props', {}).get('line_start'))
                if node.get('type') == 'link':
                    text_content = "".join(child.get('raw', '') for child in node.get('children', []) if child.get('type') == 'text')
                    current_list.append({
                        "href": node.get('link', ''), # Mistune v2 uses 'link' for href
                        "text": text_content,
                        "line": line_num,
                        # "column": ... # Harder to get accurately for links
                    })
                elif 'children' in node: # Must recurse for other block/inline elements containing links
                    for child in node['children']:
                        visitor(child, current_list)
        for root_node in ast_nodes:
            visitor(root_node, link_nodes_data)
        return link_nodes_data


    def check_links_in_doc(self, doc: ParsedDoc, project_existing_files: Set[Path]) -> List[LinkError]:
        errors: List[LinkError] = []
        if not self.config.get('link_checking', {}).get('enabled', False):
            return errors

        link_nodes = self._get_link_nodes_from_ast(doc.ast)
        for link_data in link_nodes:
            dest = link_data.get("href", "")
            text = link_data.get("text")
            line_num = link_data.get("line")

            if not dest: continue # Skip empty links

            is_external = bool(urlparse(dest).scheme) and urlparse(dest).scheme in ['http', 'https']

            if is_external:
                if not self._is_valid_external_url_format(dest):
                    errors.append(LinkError(
                        doc_path=doc.filepath, line_number=line_num,
                        link_destination=dest, link_text=text,
                        message="Invalid external URL format."))
            else: # Internal link
                try:
                    resolved_path = self._resolve_internal_link(doc.filepath, dest, doc.project_root)
                    # Check against project_existing_files (Set of full, resolved Paths)
                    # Normalization might be needed if project_existing_files are not fully resolved/normalized
                    if not resolved_path.is_file(): # Direct check on resolved_path
                        errors.append(LinkError(
                            doc_path=doc.filepath, line_number=line_num,
                            link_destination=dest, link_text=text,
                            message=f"Internal link points to a missing file: {resolved_path}"))
                except Exception as e: # Catch potential errors during path resolution
                     errors.append(LinkError(
                        doc_path=doc.filepath, line_number=line_num,
                        link_destination=dest, link_text=text,
                        message=f"Error resolving internal link: {e}"))
        return errors

    def _resolve_internal_link(self, doc_filepath: Path, link_dest: str, project_root_for_abs: Path) -> Path:
        link_path_part = link_dest.split('#', 1)[0]
        if not link_path_part: # Link is just an anchor like #my-section
            return doc_filepath # Points to the same file

        if link_path_part.startswith('/'):
            # Resolve from project_root (e.g. /docs/file.md -> project_root/docs/file.md)
            return (project_root_for_abs / link_path_part.lstrip('/')).resolve()
        else:
            # Resolve relative to current doc's directory (e.g. ../file.md)
            return (doc_filepath.parent / link_path_part).resolve()
            
    def _is_valid_external_url_format(self, url: str) -> bool:
        try:
            result = urlparse(url)
            # Check for scheme and netloc, and ensure scheme is http/https
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except ValueError: # Handles cases like urlparse('http:///example.com')
            return False

# Pydantic models for configuration (example)
class TermConsistencyConfig(BaseModel):
    enabled: bool = True
    default_case_sensitive: bool = False
    enforce_canonical_form: bool = False
    glossaries: List[str] = PydanticField(default_factory=list) # Paths relative to project_root
    defined_terms: Dict[str, TermDefinition] = PydanticField(default_factory=dict)

class LinkCheckingConfig(BaseModel):
    enabled: bool = True

class ConsistencyChecksScopeConfig(BaseModel):
    include: List[str] = PydanticField(default_factory=lambda: ["**/*.md"])
    exclude: List[str] = PydanticField(default_factory=list)

class ConsistencyChecksConfig(BaseModel):
    scope: ConsistencyChecksScopeConfig = PydanticField(default_factory=ConsistencyChecksScopeConfig)
    term_consistency: TermConsistencyConfig = PydanticField(default_factory=TermConsistencyConfig)
    link_checking: LinkCheckingConfig = PydanticField(default_factory=LinkCheckingConfig)

class MarkitectProjectConfig(BaseModel): # Top-level config model for markitect.yaml
    project_name: Optional[str] = None
    project_root: Path = Path(".") # Path relative to markitect.yaml location, or absolute
    consistency_checks: ConsistencyChecksConfig = PydanticField(default_factory=ConsistencyChecksConfig)
    # ... other configurations like 'schema_validation' from previous deliverables ...
```

This revised document provides a more refined approach for Phase 0, Deliverable 3.1, particularly strengthening the term consistency logic, configuration loading, and conceptual class interactions.Okay, I will create the new Markdown document `docs/docmodel_engine/context_awareness_syntax.md` for Phase 0, Deliverable 3.2, focusing on code syntax validation.
