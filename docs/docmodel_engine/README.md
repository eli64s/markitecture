# DocModel Engine: Technical Implementation Approach

## Reiterated Theme/Goal

The core purpose of the DocModel Engine is to provide a robust and flexible mechanism for defining, parsing, and validating the structure and content of Markdown documents based on user-defined schemas. This engine will empower users to enforce consistency and quality across their documentation, starting with the "Dynamic README" use case.

## Outline Technical Implementation Approach

### Architecture & Components

1.  **Schema Loader:**
    *   Responsible for reading schema definitions from YAML (initially) or TOML files.
    *   Parses the schema file and translates it into an internal representation using Pydantic models.
    *   Handles potential parsing errors in the schema file itself.

2.  **Markdown Parser Interface:**
    *   This component will be responsible for parsing a Markdown document into an Abstract Syntax Tree (AST).
    *   Initially, we will leverage an existing robust Markdown parsing library that provides an AST (e.g., `mistune`, `markdown-it-py`, or `commonmark`).
    *   The engine will define an interface or adapter for this parser to ensure that the rest of the system interacts with a consistent AST structure, regardless of the specific underlying library. This allows for future flexibility in swapping out parsers if needed.

3.  **Validator Engine:**
    *   Takes a Markdown AST and a loaded `DocModelSchema` as input.
    *   Traverses the AST and validates its nodes (headings, paragraphs, lists, code blocks, etc.) against the rules defined in the schema.
    *   Collects and returns a list of validation errors.

4.  **Pydantic Model Generator (Internal):**
    *   While users define schemas in YAML, internally, the Schema Loader will dynamically generate Pydantic models that represent these schemas. This is key to the "Pydantic-like power" requirement. For instance, a `section` defined in YAML will correspond to a Pydantic model instance.

### Key Data Structures (Pydantic Models for Schema Definition)

These models define the structure of the schema itself, which users will provide in YAML.

```python
from typing import List, Optional, Dict, Any, Literal, Union
from pydantic import BaseModel, Field as PydanticField, validator # Renamed Field to PydanticField
import re # For pattern validation

# --- Core Schema Primitives ---

class ValidationRule(BaseModel):
    """Defines a single validation rule for a field or structure."""
    type: Literal[
        "required",  # Element must be present (used contextually by validator)
        "minLength", # Minimum length for text content
        "maxLength", # Maximum length for text content
        "pattern",   # Regex pattern for text content
        "enum",      # Value must be one of a predefined set
        "minCount",  # Minimum number of items in a list/children
        "maxCount",  # Maximum number of items in a list/children
        "unique",    # All items in a list/children must be unique (conceptual)
        "custom"     # For future extensibility
    ]
    value: Optional[Any] = None
    message: Optional[str] = None

    @validator('value', pre=True, always=True)
    def check_value_for_type(cls, v, values):
        rule_type = values.get('type')
        if rule_type in ["minLength", "maxLength", "minCount", "maxCount"] and (v is not None and not isinstance(v, int)):
            raise ValueError(f"Value for '{rule_type}' must be an integer or None.")
        if rule_type == "pattern" and (v is not None and not isinstance(v, str)):
            raise ValueError(f"Value for 'pattern' must be a regex string or None.")
        if rule_type == "enum" and (v is not None and not isinstance(v, list)):
            raise ValueError(f"Value for 'enum' must be a list or None.")
        # 'required' type doesn't need a value in ValidationRule, it's a property of FieldDefinition
        return v

class FieldDefinition(BaseModel):
    """
    Defines a specific field within a document structure (e.g., a paragraph, a list item).
    """
    name: str
    description: Optional[str] = None
    markdown_type: Literal[ # Maps to common Markdown element types
        "Paragraph", "Heading", "List", "ListItem", "CodeBlock", "BlockQuote", "Link", "Image", "Emphasis", "Strong", "Text"
    ]
    required: bool = False # Is this field required within its parent structure?
    validations: List[ValidationRule] = PydanticField(default_factory=list)
    # For complex fields like list items that might have their own defined sub-fields.
    # This allows defining structure within, for example, each ListItem.
    fields: Optional[Dict[str, 'StructureRule']] = None # Name maps to StructureRule

class StructureRule(BaseModel):
    """
    Defines the rules for a structural element in the Markdown document,
    typically corresponding to a section, subsection, or a complex element like a list or table.
    """
    name: str
    description: Optional[str] = None
    # How to identify this structure in MD. e.g., a "Section" might start with a "Heading".
    entry_marker_type: Literal["Heading", "CustomDelimiter", "List", "ListItem", "Paragraph"] # Added more types
    entry_marker_properties: Optional[Dict[str, Any]] = None # e.g., {"level": 1, "text_pattern": "Introduction.*"} for Heading

    # Defines the expected child elements or fields within this structure.
    elements: Dict[str, Union[FieldDefinition, 'StructureRule']] = PydanticField(default_factory=dict)

    validations: List[ValidationRule] = PydanticField(default_factory=list) # e.g. min/max number of elements

    ordered: bool = False # Are the 'elements' expected in a specific order?
    element_order: Optional[List[str]] = None # List of element names in expected order if 'ordered' is true.

    allow_extra_elements: bool = True


# --- Top-level Schema ---

class DocModelSchema(BaseModel):
    """The root schema for a Markdown document model."""
    schema_name: str
    version: str
    description: Optional[str] = None
    # The top-level structural rules for the document.
    # Typically, a document is a sequence of major sections.
    structure: Dict[str, StructureRule] # Key is the logical name of the top-level section

FieldDefinition.update_forward_refs()
StructureRule.update_forward_refs()

```

### Core Function Signatures / Class Definitions

```python
from pathlib import Path
from typing import List, Any, TypeVar
import yaml

# Assuming Pydantic models are defined as above
# Placeholder for the actual AST node type from the chosen Markdown parser
MarkdownASTNode = Any # e.g., a mistune.BlockToken (which is a dict)

class ValidationError(BaseModel):
    message: str
    path_in_document: Optional[str] = None # e.g., "Introduction/Motivation/Paragraph[2]"
    schema_rule_id: Optional[str] = None # e.g., "ReadmeMaturityFramework.Introduction.minLength"


T_BaseModel = TypeVar('T_BaseModel', bound=BaseModel)

class SchemaLoader:
    @staticmethod
    def _load_yaml_data(path: Path) -> dict:
        if not path.is_file():
            raise FileNotFoundError(f"Schema file not found: {path}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML schema {path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to read schema file {path}: {e}")

    @staticmethod
    def load_yaml_schema(path: Path) -> DocModelSchema:
        data = SchemaLoader._load_yaml_data(path)
        try:
            return DocModelSchema.parse_obj(data)
        except Exception as e: # Catch Pydantic validation errors
            raise ValueError(f"Schema validation error for {path}: {e}")

class MarkdownParserAdapter: # Interface/Adapter
    def parse(self, markdown_content: str) -> List[MarkdownASTNode]: # Returns a list of top-level AST nodes
        # Example using mistune:
        # import mistune
        # Ensure mistune is installed: pip install mistune
        # md_parser = mistune.create_markdown(renderer=None) # For raw AST tokens
        # return md_parser(markdown_content)
        raise NotImplementedError("Markdown parser adapter not implemented yet.")

class ValidatorEngine:
    def __init__(self, schema: DocModelSchema):
        self.schema = schema
        self.errors: List[ValidationError] = []
        self._ast_node_type_key = 'type' # Configurable key for AST node type
        self._ast_node_children_key = 'children' # Configurable key for AST node children
        self._ast_node_text_key = 'raw' # Configurable key for raw text in text/leaf nodes (mistune)

    def _add_error(self, message: str, node: Optional[MarkdownASTNode] = None, rule_id: Optional[str] = None, element_name: Optional[str]=None):
        path_in_doc = rule_id or "Unknown"
        if element_name and rule_id and not rule_id.endswith(element_name):
             path_in_doc = f"{rule_id}.{element_name}"

        # Basic location from node if possible (highly dependent on AST)
        # For mistune, line numbers might be in `node.get('props', {}).get('line_number')` for some tokens
        # This needs a more robust location tracking mechanism.
        if node and isinstance(node, dict) and 'line_number' in node.get('props', {}):
            path_in_doc += f" (approx line {node['props']['line_number']})"
        elif node and isinstance(node, dict) and 'position' in node: # CommonMark-like position
             path_in_doc += f" (pos {node['position']})"

        self.errors.append(ValidationError(message=message, path_in_document=path_in_doc, schema_rule_id=rule_id))

    def _get_node_type(self, node: MarkdownASTNode) -> Optional[str]:
        if isinstance(node, dict):
            return node.get(self._ast_node_type_key)
        elif hasattr(node, self._ast_node_type_key): # For object-style AST nodes
            return getattr(node, self._ast_node_type_key)
        return None

    def _get_node_children(self, node: MarkdownASTNode) -> List[MarkdownASTNode]:
        if isinstance(node, dict):
            return node.get(self._ast_node_children_key, [])
        elif hasattr(node, self._ast_node_children_key):
            return getattr(node, self._ast_node_children_key, [])
        return []

    def _extract_text_content(self, node: MarkdownASTNode) -> str:
        """Extracts text content from a node or its children, tailored for mistune-like ASTs."""
        content = ""
        node_type = self._get_node_type(node)

        if isinstance(node, dict):
            if node_type == 'text' or node_type == 'inline_html': # mistune specific
                return node.get(self._ast_node_text_key, '')
            if 'children' in node: # Common for block tokens like paragraph, heading
                for child in node.get('children', []):
                    content += self._extract_text_content(child)
            elif self._ast_node_text_key in node : # e.g. code_block content
                return node.get(self._ast_node_text_key, '')

        elif isinstance(node, str): # Should not happen with mistune block tokens
            return node
        return content.strip()


    def _node_matches_element_rule(self, node: MarkdownASTNode, rule: Union[FieldDefinition, StructureRule]) -> bool:
        ast_node_type = self._get_node_type(node)
        if not ast_node_type: return False
        ast_node_type = ast_node_type.lower()

        rule_marker_type = ""
        if isinstance(rule, FieldDefinition):
            rule_marker_type = rule.markdown_type.lower()
        elif isinstance(rule, StructureRule):
            rule_marker_type = rule.entry_marker_type.lower()

        if ast_node_type != rule_marker_type:
            return False

        # Specific property checks for StructureRules (e.g., heading level)
        if isinstance(rule, StructureRule) and rule.entry_marker_properties:
            if rule.entry_marker_type == "Heading": # Common case
                expected_level = rule.entry_marker_properties.get("level")
                text_pattern = rule.entry_marker_properties.get("text_pattern")

                actual_level = node.get('level') if isinstance(node, dict) else getattr(node, 'level', None)

                level_match = (expected_level is None or actual_level == expected_level)
                if not level_match: return False

                if text_pattern:
                    node_text = self._extract_text_content(node)
                    if not re.search(text_pattern, node_text): return False
                return True # All checks passed for Heading

        return True # Type matched, and no further properties to check or they passed

    def _validate_field_content(self, node: MarkdownASTNode, field_def: FieldDefinition, rule_id_path: str):
        node_content = self._extract_text_content(node)

        for v_rule in field_def.validations:
            rule_type_path = f"{rule_id_path}.{field_def.name}.{v_rule.type}"
            if v_rule.type == "minLength":
                if len(node_content) < v_rule.value:
                    self._add_error(v_rule.message or f"Content too short (min {v_rule.value}, got {len(node_content)}).", node, rule_type_path)
            elif v_rule.type == "maxLength":
                if len(node_content) > v_rule.value:
                    self._add_error(v_rule.message or f"Content too long (max {v_rule.value}, got {len(node_content)}).", node, rule_type_path)
            elif v_rule.type == "pattern":
                if not re.search(v_rule.value, node_content):
                    self._add_error(v_rule.message or f"Content does not match pattern '{v_rule.value}'.", node, rule_type_path)
            # TODO: Implement other validation types like 'enum', 'minCount/maxCount' (for list items or children)

    def _validate_elements_list(self, ast_nodes_list: List[MarkdownASTNode], elements_schema: Dict[str, Union[FieldDefinition, StructureRule]],
                                 ordered: bool, element_order: Optional[List[str]], allow_extra: bool, base_rule_id: str):

        processed_indices = set()
        expected_elements_map = elements_schema.copy() # name -> Rule
        current_ast_idx = 0

        if ordered and element_order:
            for i, expected_name in enumerate(element_order):
                element_rule = elements_schema.get(expected_name)
                if not element_rule: # Schema error
                    self._add_error(f"Schema error: Ordered element '{expected_name}' not in schema definition.", rule_id=f"{base_rule_id}.{expected_name}")
                    continue

                found_ordered_match = False
                # Try to find this ordered element starting from current_ast_idx
                search_idx = current_ast_idx
                while search_idx < len(ast_nodes_list):
                    if search_idx in processed_indices: # Should not happen if current_ast_idx is managed well
                        search_idx += 1
                        continue

                    current_node = ast_nodes_list[search_idx]
                    if self._node_matches_element_rule(current_node, element_rule):
                        # Found the expected element
                        del expected_elements_map[expected_name]
                        processed_indices.add(search_idx)

                        element_path_id = f"{base_rule_id}.{expected_name}"
                        if isinstance(element_rule, FieldDefinition):
                            self._validate_field_content(current_node, element_rule, element_path_id)
                            # If FieldDefinition has 'fields', it implies complex content (e.g. list item with structure)
                            if element_rule.fields:
                                # This would treat the 'current_node' (e.g. a ListItem) as a parent for these fields
                                # The children for these fields would come from current_node's children.
                                self._validate_elements_list(self._get_node_children(current_node), element_rule.fields,
                                                             False, None, True, # Example: fields within a list item are often unordered
                                                             element_path_id)
                        elif isinstance(element_rule, StructureRule):
                            # Determine children for this structure rule (slice of ast_nodes_list)
                            # This is the tricky part for flat ASTs: defining scope.
                            # For now, assume direct children if AST is nested, or pass limited subsequent nodes.
                            structure_children, consumed_count = self._get_nodes_for_structure(ast_nodes_list[search_idx+1:], element_rule)
                            self._validate_elements_list(structure_children, element_rule.elements,
                                                         element_rule.ordered, element_rule.element_order,
                                                         element_rule.allow_extra_elements, element_path_id)
                            # Advance processed_indices by consumed_count for the structure's children
                            for k in range(consumed_count):
                                processed_indices.add(search_idx + 1 + k)


                        current_ast_idx = search_idx + 1 # Next search starts after this matched node
                        found_ordered_match = True
                        break # Move to the next element in element_order
                    search_idx += 1 # Current node didn't match, try next node for the SAME ordered element

                if not found_ordered_match:
                    is_required = getattr(element_rule, 'required', False) if isinstance(element_rule, FieldDefinition) else True # StructureRule assumed required
                    if is_required:
                        self._add_error(f"Required ordered element '{expected_name}' not found or out of sequence.", rule_id=f"{base_rule_id}.{expected_name}.required")

        # Process remaining nodes for unordered elements or if not ordered at all
        for i in range(len(ast_nodes_list)): # Iterate using current_ast_idx if order matters and some were processed
            if i in processed_indices:
                continue

            current_node = ast_nodes_list[i]
            found_unordered_match = False
            for name, element_rule in list(expected_elements_map.items()): # list() for safe deletion
                if self._node_matches_element_rule(current_node, element_rule):
                    del expected_elements_map[name]
                    processed_indices.add(i)
                    element_path_id = f"{base_rule_id}.{name}"

                    if isinstance(element_rule, FieldDefinition):
                        self._validate_field_content(current_node, element_rule, element_path_id)
                        if element_rule.fields:
                             self._validate_elements_list(self._get_node_children(current_node), element_rule.fields,
                                                          False, None, True, element_path_id)
                    elif isinstance(element_rule, StructureRule):
                        structure_children, consumed_count = self._get_nodes_for_structure(ast_nodes_list[i+1:], element_rule)
                        self._validate_elements_list(structure_children, element_rule.elements,
                                                     element_rule.ordered, element_rule.element_order,
                                                     element_rule.allow_extra_elements, element_path_id)
                        for k in range(consumed_count):
                            processed_indices.add(i + 1 + k)

                    found_unordered_match = True
                    break # Matched this node, move to next AST node

            if not found_unordered_match and not allow_extra:
                node_type_str = self._get_node_type(current_node) or "UnknownType"
                self._add_error(f"Unexpected element of type '{node_type_str}'.", current_node, f"{base_rule_id}.allow_extra_elements")

        # Check for any remaining required elements that were not found
        for name, rule_def in expected_elements_map.items():
            is_required = getattr(rule_def, 'required', False) if isinstance(rule_def, FieldDefinition) else True # StructureRule assumed required
            if is_required:
                self._add_error(f"Required element '{name}' not found.", rule_id=f"{base_rule_id}.{name}.required")


    def _get_nodes_for_structure(self, sibling_nodes: List[MarkdownASTNode], structure_rule: StructureRule) -> (List[MarkdownASTNode], int):
        """
        Heuristically determines the list of AST nodes that belong to a given StructureRule
        from a list of subsequent sibling nodes. This is crucial for flat ASTs.
        Returns the list of nodes and the number of sibling_nodes consumed.
        """
        content_nodes = []
        consumed_count = 0
        # If structure is, e.g., a Heading-defined section, content ends before next same/higher heading.
        if structure_rule.entry_marker_type == "Heading":
            current_level = structure_rule.entry_marker_properties.get("level", 0) # Level of the structure's entry heading
            for node in sibling_nodes:
                consumed_count += 1
                node_type = self._get_node_type(node)
                if node_type and node_type.lower() == "heading":
                    node_level = node.get('level') if isinstance(node, dict) else getattr(node, 'level', 100)
                    if node_level <= current_level:
                        consumed_count -=1 # This node is not part of current structure
                        break # End of section
                content_nodes.append(node)
            return content_nodes, consumed_count

        # For other types like List, the list token itself contains its items as children typically.
        # If entry_marker_type is List, its elements (ListItems) are usually direct children.
        # This function is more for sections/blocks in a flat list.
        # Default: assume all subsequent siblings are part of it (simplistic, needs refinement)
        return sibling_nodes, len(sibling_nodes)


    def validate_ast(self, ast_root_list: List[MarkdownASTNode]) -> List[ValidationError]:
        self.errors = []
        # The document itself is treated as a sequence of top-level structures.
        self._validate_elements_list(
            ast_nodes_list=ast_root_list,
            elements_schema=self.schema.structure, # Top-level structure rules from schema
            ordered=True, # Assume top-level sections are ordered by default as per schema definition
            element_order=list(self.schema.structure.keys()), # Order is schema definition order
            allow_extra=False, # Typically, no extra top-level sections allowed unless schema specifies
            base_rule_id=self.schema.schema_name
        )
        return self.errors

```

## Adherence to Principles

*   **Schema-First:** The Pydantic models (`DocModelSchema`, `StructureRule`, `FieldDefinition`) are the canonical, internal representation of the schema. YAML/TOML files are serialization formats for these models.
*   **Pydantic-like Power:**
    *   **Types:** `FieldDefinition.markdown_type`, Pydantic types (`str`, `int`, `List`, `Literal`), and `StructureRule.entry_marker_type` enforce type constraints.
    *   **Required/Optional:** `FieldDefinition.required` and Pydantic's `Optional` handle presence.
    *   **Simple Constraints:** `ValidationRule` (e.g., `minLength`, `pattern`) and Pydantic's `@validator` (used in schema models for self-consistency) provide constraint mechanisms.

## Application to Dynamic README Scenario

### 1. `markitect_schema_ReadmeMaturityFramework.yaml`

This schema defines the structure for a comprehensive, "mature" README.

**Example `markitect_schema_ReadmeMaturityFramework.yaml` (Conceptual Snippet):**

```yaml
schema_name: ReadmeMaturityFramework
version: "1.0"
description: "Defines the structure for a mature and comprehensive README file."

structure:
  Introduction:
    name: Introduction # Logical name for this section
    description: "High-level overview of the project."
    entry_marker_type: Heading # This section must start with a Heading
    entry_marker_properties:
      level: 1 # The Heading must be H1
      # text_pattern: "^(Introduction|Overview|About)" # Optional: regex for heading text
    elements: # Child elements expected within the Introduction section
      ProjectPurpose:
        name: ProjectPurpose
        markdown_type: Paragraph # Expected to be a paragraph
        required: true
        validations:
          - type: minLength
            value: 50
            message: "The project purpose description should be at least 50 characters."
      KeyFeatures: # Another element within Introduction
        name: KeyFeatures
        entry_marker_type: List # This is a list structure
        required: false
        # elements for a List structure would define rules for its ListItems
        # For example, each ListItem could be a FieldDefinition or another StructureRule
        elements:
          FeatureItem:
            name: FeatureItem # Logical name for items in this list
            entry_marker_type: ListItem # Defines the rule for each item in KeyFeatures list
            required: true # Implies minCount: 1 for the list if KeyFeatures is present
            # Further define what a FeatureItem contains, e.g., a Paragraph
            elements:
              ItemText:
                name: ItemText
                markdown_type: Paragraph # Each list item should be a paragraph
                required: true
                validations:
                  - type: minLength
                    value: 10
        validations: # Validations on the KeyFeatures list itself
          - type: minCount # If KeyFeatures list is present, it must have at least 2 items.
            value: 2
    ordered: true # Elements within Introduction must appear in this order
    element_order: ["ProjectPurpose", "KeyFeatures"]
    allow_extra_elements: false # No other major elements allowed directly under Introduction heading

  Installation:
    name: Installation
    description: "Instructions on how to install the project."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 2
      text_pattern: "^Installation$"
    elements:
      Prerequisites:
        name: Prerequisites
        markdown_type: Paragraph
        required: false
      Steps:
        name: Steps
        entry_marker_type: List # This is a list of installation steps
        required: true
        elements:
          StepItem: # Rule for each step in the list
            name: StepItem
            entry_marker_type: ListItem
            elements:
              Instruction:
                name: Instruction
                markdown_type: Paragraph # Or CodeBlock if steps are commands
                required: true
    ordered: true
    element_order: ["Prerequisites", "Steps"]
  # ... other sections like Usage, Contributing, License ...
```

### 2. `MyProjectReadmeStub.yaml`

A simpler schema for a basic project README.

**Example `MyProjectReadmeStub.yaml`:**

```yaml
schema_name: MyProjectReadmeStub
version: "0.1"
description: "A basic README structure for MyProject."

structure:
  ProjectTitle:
    name: ProjectTitle
    description: "The main title of the project, must be an H1."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 1
    # A heading itself doesn't have 'elements' for its text content.
    # Its text content would be validated by a 'pattern' or 'maxLength'
    # validation directly on the ProjectTitle StructureRule if needed, or by a
    # specific 'Text' FieldDefinition if we model heading content explicitly.
    # For simplicity, we assume the heading's existence and level are key.
    # If specific text validation for the heading is needed, add to 'validations' of ProjectTitle.
    validations:
      - type: pattern # Example: Ensure title is not just whitespace
        value: "\\S+" # Must contain non-whitespace
        message: "Project title cannot be empty."
    elements: {} # No sub-elements defined for the H1 itself

  QuickDescription:
    name: QuickDescription
    description: "A short, one-paragraph description immediately following the title."
    # This is tricky: needs to be the *first* paragraph after ProjectTitle.
    # Schema could define it as a Paragraph type that must directly follow ProjectTitle.
    entry_marker_type: Paragraph
    required: true
    # elements: {} # Assuming the paragraph's content itself is validated directly by 'validations'
    validations: # These apply to the content of the QuickDescription paragraph
      - type: minLength
        value: 20
      - type: maxLength
        value: 200
    # No 'elements' needed if it's just a simple paragraph whose text is validated.
```

### Python Code Snippets

**Pydantic Models for Internal Schema Representation:**
*(Provided in "Key Data Structures" section above)*

**Example `markitect_schema_ReadmeMaturityFramework.yaml` & `MyProjectReadmeStub.yaml`:**
*(Provided above)*

**Python Code for Schema Loading (Conceptual `SchemaLoader`):**
```python
# (SchemaLoader class as defined in "Core Function Signatures / Class Definitions")

# --- Example Usage ---
# if __name__ == "__main__":
#     try:
#         # Create dummy YAML for testing SchemaLoader
#         Path("dummy_schema.yaml").write_text("""
# schema_name: DummySchemaForLoading
# version: "0.1"
# description: "A test schema."
# structure:
#   MySection:
#     name: MySection
#     entry_marker_type: Heading
#     entry_marker_properties: {level: 1}
#     elements:
#       MyParagraph:
#         name: MyParagraph
#         markdown_type: Paragraph
#         required: true
#         validations:
#           - type: minLength
#             value: 10
#     ordered: true
#     element_order: ["MyParagraph"]
#         """)
#
#         schema_path = Path("dummy_schema.yaml")
#         loaded_schema = SchemaLoader.load_yaml_schema(schema_path)
#         print(f"Successfully loaded schema: {loaded_schema.schema_name} (v{loaded_schema.version})")
#         print(f"First section name: {list(loaded_schema.structure.keys())[0]}")
#         # print(loaded_schema.structure["MySection"].elements["MyParagraph"].name)
#
#     except (FileNotFoundError, ValueError, RuntimeError) as e:
#         print(f"Error during schema loading example: {e}")
#     finally:
#         if Path("dummy_schema.yaml").exists():
#             Path("dummy_schema.yaml").unlink()
```

**Conceptual Python Code for AST Validation (`ValidatorEngine`):**
```python
# (ValidatorEngine class and its methods as defined in "Core Function Signatures / Class Definitions")
# --- Example Usage (Conceptual with mistune) ---
# import mistune # Ensure mistune is installed

# if __name__ == "__main__":
#     # 1. Define and Load Schema (using dummy_schema.yaml from SchemaLoader example)
#     Path("dummy_schema.yaml").write_text("""
# schema_name: TestValidationSchema
# version: "1.0"
# structure:
#   MainHeading:
#     name: MainHeading
#     entry_marker_type: Heading
#     entry_marker_properties: {level: 1}
#     elements: {} # No further elements, just validating the heading itself
#   IntroParagraph:
#     name: IntroParagraph
#     entry_marker_type: Paragraph # Note: 'entry_marker_type' for FieldDefinition-like use here
#     required: true
#     validations:
#       - type: minLength
#         value: 10
#         message: "Intro paragraph is too short."
#     """) # Simplified schema for validation testing
#     schema_path = Path("dummy_schema.yaml")
#     doc_schema: Optional[DocModelSchema] = None
#     try:
#         doc_schema = SchemaLoader.load_yaml_schema(schema_path)
#     except Exception as e:
#         print(f"Schema loading failed: {e}")
#         exit()

#     # 2. Initialize Parser and Validator
#     # In a real scenario, MarkdownParserAdapter would be implemented
#     # For this example, we'll manually create mistune ASTs.
#     md_parser = mistune.create_markdown(renderer=None) # Raw AST tokens
#     validator = ValidatorEngine(doc_schema)

#     # 3. Test Cases
#     test_cases = {
#         "Valid": "# MainHeading\n\nThis is a sufficiently long intro paragraph.",
#         "Missing Paragraph": "# MainHeading",
#         "Paragraph too short": "# MainHeading\n\nToo short.",
#         "Wrong Heading Level": "## MainHeading\n\nThis is a good paragraph.",
#         "Extra Element": "# MainHeading\n\nThis is good.\n\n* Unexpected item"
#     }

#     for name, md_content in test_cases.items():
#         print(f"\n--- Validating Test Case: {name} ---")
#         ast = md_parser(md_content) # List of dicts
#         errors = validator.validate_ast(ast)
#         if not errors:
#             print("Validation Succeeded (No errors found).")
#         else:
#             print("Validation Failed:")
#             for error in errors:
#                 print(f"  - Message: {error.message}")
#                 print(f"    Path: {error.path_in_document}")
#                 # print(f"    Rule ID: {error.schema_rule_id}") # Redundant if path includes it
#
#     if Path("dummy_schema.yaml").exists():
#         Path("dummy_schema.yaml").unlink()
```

This technical approach document lays the groundwork for the DocModel Engine, focusing on schema definition, loading, and the core validation logic against Markdown ASTs. The Pydantic models provide the "schema-first" backbone, and the conceptual `ValidatorEngine` illustrates the path to comparing parsed Markdown to these schemas. Full implementation of the `ValidatorEngine` will be iterative and tightly coupled with the chosen Markdown parser's AST specifics.The technical implementation approach document has been updated in `docs/docmodel_engine/README.md`.

I have addressed the key requirements:
1.  **User-defined schemas:** YAML examples are provided, and the `SchemaLoader` is designed for YAML.
2.  **Pydantic-like power:** Pydantic models with type hints, `Optional`, `Literal`, `default_factory`, and custom validators (`ValidationRule`) demonstrate this.
3.  **Core parsing and validation logic:** The architecture includes a `MarkdownParserAdapter` (interface) and a `ValidatorEngine`. The `ValidatorEngine`'s conceptual implementation details how an AST would be traversed and validated against the schema, including matching nodes to rules, validating content, and handling ordered/unordered elements.
4.  **Adherence to "Schema-First" principle:** The document emphasizes that Pydantic models are the canonical internal representation of the schemas.
5.  **Application to Dynamic README Scenario:**
    *   Example YAML for `markitect_schema_ReadmeMaturityFramework.yaml` and `MyProjectReadmeStub.yaml` are provided.
    *   The Pydantic models in the "Key Data Structures" section are what would be generated internally.
    *   Example Python code for `SchemaLoader` and a conceptual `ValidatorEngine` (with example usage) illustrate loading and validation.

The structure of the output follows the requested format. Code snippets for Pydantic models, YAML schemas, schema loading, and conceptual AST validation are included.
The `ValidatorEngine` has been significantly detailed to outline the logic for matching AST nodes to schema rules, handling element order, required fields, and extra elements, along with a more refined approach to extracting content and identifying structure within potentially flat ASTs (like those from `mistune`).

This completes Phase 0, Deliverable 1.
