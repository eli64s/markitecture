# Advanced DocModel Engine (Phase 1, Deliverable 1 - FR1.4)

## Reiterated Theme/Goal

The goal of this phase for the DocModel Engine is to significantly enhance its flexibility and expressive power. This involves introducing mechanisms for schema reuse (inheritance and composition) and expanding the range of validation rules available to schema designers. These advancements will allow users to create more sophisticated, maintainable, and robust document models, leading to higher quality and consistency in their documentation suites.

## Technical Implementation Approach

### Schema Inheritance and Composition

This feature allows a DocModel schema to be built upon or include parts of other schemas, promoting reusability and modularity.

**1. Proposed YAML Syntax:**

We'll introduce an `extends` keyword for inheritance (single parent) and an `includes` keyword for composition (mixing in multiple fragments or partial schemas).

*   **Inheritance (`extends`):**
    A schema can inherit from a single base schema. The inheriting schema automatically gets all `structure` elements and global properties (like `version`, `description` if not overridden) from the base. It can then add new elements, override existing elements (by defining an element with the same name), or modify properties of inherited elements (though full modification of inherited elements might be complex and start with simple overrides).

    ```yaml
    # base_page_schema.yaml
    schema_name: BasePage
    version: "1.0"
    description: "A base page schema with common frontmatter requirements."
    # Defines expected top-level keys in frontmatter for all pages inheriting this
    frontmatter_schema: # New section for frontmatter validation rules
      fields:
        title: { markdown_type: Text, required: true, validations: [{type: minLength, value: 5}] }
        author: { markdown_type: Text, required: false }
    structure:
      CommonFooter:
        name: CommonFooter
        entry_marker_type: Heading # Or a custom delimiter
        entry_marker_properties: { level: 4, text_pattern: "^(Footer|Acknowledgements)$" }
        elements:
          CopyrightNotice: { name: CopyrightNotice, markdown_type: Paragraph, required: true }
    ```

    ```yaml
    # tutorial_page_schema.yaml
    schema_name: TutorialPage
    extends: "./base_page_schema.yaml" # Path relative to this file or project root
    version: "1.1" # Overrides base version
    description: "Schema for a tutorial page, inheriting from BasePage."
    frontmatter_schema: # Can extend or override base frontmatter
      fields: # title and author are inherited implicitly
        difficulty: { markdown_type: Text, required: true, validations: [{type: enum, value: ["beginner", "intermediate", "advanced"]}]}
        tags: { markdown_type: List, element_schema: {markdown_type: Text} } # Example of a list in frontmatter
    structure:
      # Inherits CommonFooter from BasePage
      TutorialGoal:
        name: TutorialGoal
        entry_marker_type: Heading
        entry_marker_properties: { level: 2, text_pattern: "^Goal$" }
        elements:
          GoalDescription: { name: GoalDescription, markdown_type: Paragraph, required: true }
      # Override CommonFooter if needed (by redefining it)
      # CommonFooter:
      #   name: CommonFooter
      #   entry_marker_type: Heading
      #   entry_marker_properties: { level: 4, text_pattern: "^Tutorial Footer$" } # Modified pattern
      #   elements:
      #     CopyrightNotice: { name: CopyrightNotice, markdown_type: Paragraph, required: true }
      #     TutorialFeedbackLink: { name: TutorialFeedbackLink, markdown_type: Paragraph, required: false }
    ```

*   **Composition (`includes`):**
    A schema can include one or more "schema fragments" or partial schemas. An included fragment is typically a collection of `StructureRule` or `FieldDefinition` definitions that are merged into the including schema's `structure` or a specific element's `elements`.

    ```yaml
    # code_examples_fragment.yaml
    # This fragment defines a set of common structure rules for code examples
    # It's not a full schema itself (no schema_name, version etc.)
    CodeBlockWithCaption:
      name: CodeBlockWithCaption # This name will be the key when included
      entry_marker_type: Paragraph # Assume caption precedes code block
      elements:
        Caption: { name: Caption, markdown_type: Text, required: true } # From the paragraph
        Code: { name: Code, markdown_type: CodeBlock, required: true }
    
    PythonCodeExample:
      name: PythonCodeExample
      # Could potentially 'extend' CodeBlockWithCaption if fragments supported it,
      # or just be a specific configuration.
      entry_marker_type: Paragraph
      elements:
        Caption: { name: Caption, markdown_type: Text, required: false }
        Code: { name: Code, markdown_type: CodeBlock, required: true, language: "python" } # Specific language
    ```

    ```yaml
    # main_api_doc_schema.yaml
    schema_name: APIDocumentation
    version: "1.0"
    includes: # List of paths to fragments or named fragments from a library
      - "./code_examples_fragment.yaml" 
      # - "standard_library_fragments/table_structures.yaml" # Future concept
    structure:
      EndpointOverview:
        name: EndpointOverview
        # ...
      PythonSample: # User wants to use the PythonCodeExample fragment here
        # This is a reference to an element defined in an included fragment.
        # The schema loader would need to resolve this.
        # Option A: Direct reference (if fragment keys are globally unique within includes)
        # type: PythonCodeExample # Not standard, how to make this work?
        # Option B: Merging. The 'includes' at top level makes elements from fragments
        # available to be used or overridden in the 'structure' below.
        # So, 'PythonCodeExample' (from fragment) is now a top-level structure rule here.
        # This means the fragment's top-level keys are merged into the 'structure' namespace.
        # This is the simplest merge strategy for Phase 1.
        # So, after loading includes, the effective available structures are:
        # EndpointOverview, CodeBlockWithCaption, PythonCodeExample
        # The user can then choose to use them or override them:

      MyPythonAPIExample: # User renames/wraps the fragment for specific use
        # This is a new StructureRule defined in this schema
        name: MyPythonAPIExample 
        entry_marker_type: Heading
        entry_marker_properties: { level: 3, text_pattern: "Python API Usage" }
        # It 'embeds' or 'uses' the structure from the fragment by redefining it
        # and referencing the fragment's elements or by a special "use_fragment_element" key.
        # Simpler for Phase 1: Assume `includes` merges definitions. If a key in `structure`
        # matches a key from an included fragment, it's an override. Otherwise, included keys
        # are available as if defined directly.
        # Let's refine: `includes` makes definitions available. If you want to use one:
      UsagePython: { $ref: "#/components/structures/PythonCodeExample" } # JSON Schema-like ref
      # Or simpler:
      # UsagePython: { use_structure: PythonCodeExample } # Markitect specific
      # For Phase 1, let's go with: `includes` merges directly into the `structure` definitions.
      # The key from the fragment file becomes a key in the `structure` of the current schema.
      # So, after `includes: ["./code_examples_fragment.yaml"]`, the APIDocumentation schema
      # effectively has `CodeBlockWithCaption` and `PythonCodeExample` as part of its `structure`.
      # The user can then reference them or let them be as top-level sections.
      # To place them *within* another element, they'd need to be redefined or copied.

      # Refined approach for `includes`:
      # `includes` makes named definitions available in a "components" section.
      # components:
      #   structures: # Populated from includes
      #     CodeBlockWithCaption: { ... from fragment ... }
      #     PythonCodeExample: { ... from fragment ... }
      # structure:
      #   MyPythonSample:
      #     name: MyPythonSample
      #     # ...
      #     elements:
      #       ActualCode: { $ref: "#/components/structures/PythonCodeExample" }
      # This is powerful but adds complexity.
      # Phase 1 simpler approach for `includes`:
      # Top-level keys from included YAML files are merged into the `structure` dict.
      # Order matters: later includes or direct definitions can override earlier ones if keys clash.
```
**Revised Simpler `includes` for Phase 1:**
An `include` directive will merge the top-level keys (expected to be `StructureRule` definitions) from the included file into the `structure` of the current schema. If keys conflict, the later definition (either from a later include or defined directly in the current schema) wins.

```yaml
# main_api_doc_schema.yaml
schema_name: APIDocumentation
version: "1.0"
includes:
  - "./code_examples_fragment.yaml" # Provides CodeBlockWithCaption, PythonCodeExample
structure:
  EndpointOverview:
    name: EndpointOverview
    # ...
  # Now CodeBlockWithCaption and PythonCodeExample are available as if defined here.
  # A document can have a section that matches the "PythonCodeExample" structure rule.
  # If we want to use PythonCodeExample *inside* another element, we'd copy its definition:
  DetailedPythonUsage:
    name: DetailedPythonUsage
    entry_marker_type: Heading
    entry_marker_properties: {level: 3, text_pattern: "Detailed Python"}
    elements:
      # Manually copy/adapt structure from PythonCodeExample for now.
      # Future: { $ref: "PythonCodeExample" } or similar.
      TheCaption: { name: TheCaption, markdown_type: Text, required: false }
      TheCode: { name: TheCode, markdown_type: CodeBlock, required: true, language: "python" }
```

**2. Schema Loading and Resolution Logic:**

The `SchemaLoader` (from Phase 0) will be updated:

*   **Detection:** When loading a schema YAML, it checks for `extends` or `includes` keys.
*   **`extends` (Inheritance):**
    1.  If `extends: path/to/base_schema.yaml` is found:
        *   Recursively call `SchemaLoader` to load the base schema first. If the base also extends another schema, this process continues up the chain. Circular dependencies must be detected and result in an error.
        *   Once the base schema object (`DocModelSchema` Pydantic model) is loaded, the current schema's properties are merged onto it.
        *   **Merge Strategy:**
            *   Scalar properties (`schema_name`, `version`, `description`): Current schema's values override base's.
            *   `frontmatter_schema`: Fields are merged. If a field with the same name exists, the current schema's field definition overrides the base's. New fields are added.
            *   `structure` (Dictionary of `StructureRule`s): StructureRules are merged by key.
                *   If a key exists in both base and current, the current schema's `StructureRule` definition *completely overrides* the base's for that key. (Simpler for Phase 1 than deep merging rules within a StructureRule).
                *   New keys from the current schema are added.
                *   StructureRules only in the base are retained.
            *   `allow_extra_elements` and other global flags: Current schema overrides base.
*   **`includes` (Composition):**
    1.  If `includes: [path1, path2]` is found:
        *   For each path in the list, load the YAML file. These files are expected to be "fragments" – essentially dictionaries where keys are intended `StructureRule` names and values are their definitions. They are NOT full `DocModelSchema` files.
        *   The top-level keys and their definitions from each included fragment are merged into the current schema's `structure` dictionary.
        *   **Merge Strategy (Order of Precedence for `structure` dictionary):**
            1.  Definitions from the schema file with `extends` (base schema).
            2.  Definitions from files in `includes`, processed in the order they appear. Later includes override earlier ones if keys clash.
            3.  Direct definitions in the `structure` block of the current schema file. These override anything from `extends` or `includes`.
*   **Path Resolution:** Paths in `extends` and `includes` should be resolved relative to the current schema file's location or relative to the project root if prefixed appropriately (e.g., `project://schemas/base.yaml`).
*   **Caching:** Loaded base schemas and fragments should be cached by the `SchemaLoader` during a validation run to avoid redundant parsing and processing if they are referenced multiple times.

**3. Conflict Resolution Strategy:**

*   **`extends`:** Child schema's properties and structure rule definitions (for rules with the same name) always override the parent's. There's no deep merging of individual rule properties within a `StructureRule` for Phase 1 to keep it simple; override is at the level of the entire `StructureRule` keyed by its name.
*   **`includes`:** For structure rules merged from fragments, if multiple fragments define a structure rule with the same name, the one from the fragment listed later in the `includes` list takes precedence. Definitions in the main schema file's `structure` block always override any identically named rules from included fragments.
*   **Error Reporting:** Clear errors should be reported for:
    *   Missing `extends` or `includes` files.
    *   Circular `extends` dependencies.
    *   Parsing errors in base schemas or included fragments.

**4. Pydantic Schema Model Updates:**

```python
# From Phase 0 DocModel Definition
# class DocModelSchema(BaseModel):
#     schema_name: str
#     version: str
#     description: Optional[str] = None
#     structure: Dict[str, StructureRule]

# --- Updated for Phase 1 ---
class FrontmatterFieldDefinition(BaseModel): # Simplified version of FieldDefinition for Frontmatter
    # Similar to FieldDefinition but tailored for frontmatter values (often scalar or simple lists)
    name: str # Implicitly the key in frontmatter
    description: Optional[str] = None
    # For frontmatter, markdown_type isn't directly applicable in the same way.
    # Instead, we'd use Pydantic types or simple literals.
    value_type: Literal["Text", "Number", "Boolean", "List", "Date"] # Example types
    required: bool = False
    validations: List[ValidationRule] = PydanticField(default_factory=list) # Reusing ValidationRule

class FrontmatterSchema(BaseModel):
    # Defines rules for a document's frontmatter
    fields: Dict[str, FrontmatterFieldDefinition] = PydanticField(default_factory=dict)
    # allow_extra_fields: bool = True # Future: control undefined keys in frontmatter

class DocModelSchema(BaseModel): # Updated
    schema_name: str
    version: str
    description: Optional[str] = None
    
    extends: Optional[str] = None # Path to a base schema YAML
    includes: List[str] = PydanticField(default_factory=list) # List of paths to fragment YAMLs

    frontmatter_schema: Optional[FrontmatterSchema] = None # New for structured frontmatter validation

    # Structure rules defined directly in this schema or merged from extends/includes
    structure: Dict[str, StructureRule] = PydanticField(default_factory=dict) 
    
    # Place to store merged definitions from includes for referencing (more advanced)
    # components: Optional[Dict[str, Dict[str, Union[StructureRule, FieldDefinition]]]] = None

    # Internal field, not from YAML, but populated after loading extends/includes
    # _effective_structure: Dict[str, StructureRule] = PydanticField(default_factory=dict, exclude=True)
```

### Advanced Validation Rules

**1. Regex Matching:**

*   **Pydantic Model Changes (`FieldDefinition` and `ValidationRule`):**
    *   The `ValidationRule` model from Phase 0 already supports a `pattern` type. We ensure its usage is robust.
    ```python
    # ValidationRule from Phase 0 (relevant part)
    # class ValidationRule(BaseModel):
    #    type: Literal[..., "pattern", ...]
    #    value: Optional[Any] = None # For "pattern", value is the regex string
    #    message: Optional[str] = None
    ```
    No direct change is needed in `FieldDefinition` itself if `ValidationRule(type="pattern", value="...")` is used in its `validations` list.

*   **Validation Logic (`ValidatorEngine`):**
    *   When validating a field that has a `ValidationRule` of type `pattern`:
        *   The `ValidatorEngine` will use `re.match()` or `re.search()` (configurable, `re.fullmatch()` is often best for field validation) against the field's extracted text content.
        *   The regex pattern is taken from `ValidationRule.value`.
        *   If the pattern does not match, a validation error is generated.
        *   Regex compilation (`re.compile()`) should be used for patterns if they are applied repeatedly, for performance.

**2. Enums (Allowed Values):**

*   **Pydantic Model Changes (`FieldDefinition` and `ValidationRule`):**
    *   The `ValidationRule` model from Phase 0 already supports an `enum` type.
    ```python
    # ValidationRule from Phase 0 (relevant part)
    # class ValidationRule(BaseModel):
    #    type: Literal[..., "enum", ...]
    #    value: Optional[Any] = None # For "enum", value is a list of allowed values
    #    message: Optional[str] = None
    ```

*   **Validation Logic (`ValidatorEngine`):**
    *   When validating a field with an `enum` validation rule:
        *   The field's extracted text content is checked against the list of allowed values in `ValidationRule.value`.
        *   Comparison can be case-sensitive or case-insensitive based on a new optional property in `ValidationRule` (e.g., `case_sensitive_enum: bool = True`) or a global config. For Phase 1, assume case-sensitive by default for enums.
        *   If the content is not in the allowed list, a validation error is reported.

**3. Conditional Logic (Basic "if-then-required"):**

*   **Feasibility:** Full conditional logic (`if X then Y else Z`) is complex. For Phase 1, a very basic form is proposed: "If field `A` (antecedent) has a specific value (or is present), then field `B` (consequent) is required."
*   **Proposed Schema Representation:**
    Introduce a new validation rule type or a dedicated section within `StructureRule` or `FieldDefinition`. Let's try adding it to `StructureRule`'s `validations` for now, as it often involves relationships between elements.

    ```python
    # In StructureRule.validations or FieldDefinition.validations
    # class ValidationRule(BaseModel):
    #    type: Literal[..., "conditionalRequired", ...]
    #    value: Optional[Any] # For conditionalRequired, this needs a structure
    #    message: Optional[str] = None

    # New model for the 'value' of a 'conditionalRequired' rule
    class ConditionalRequirementValue(BaseModel):
        if_element_exists: Optional[str] = None # Name of the antecedent element/field
        if_element_has_value: Optional[Any] = None # Specific value for the antecedent (optional)
        # if_element_matches_pattern: Optional[str] = None # Future: regex match on antecedent
        
        then_element_is_required: str # Name of the consequent element/field that becomes required
        # then_element_must_have_value: Optional[Any] = None # Future: require specific value for consequent
    ```
    So, a `ValidationRule` would look like:
    ```yaml
    # In a StructureRule's 'validations' list:
    # - type: conditionalRequired
    #   value:
    #     if_element_exists: "FeatureToggleX" # Name of a boolean-like field/element
    #     # if_element_has_value: true # Optional: check for specific value, e.g. if FeatureToggleX is true
    #     then_element_is_required: "FeatureToggleX_Details"
    #   message: "If FeatureToggleX is present/true, FeatureToggleX_Details must be provided."
    ```
    This rule would typically apply to the parent `StructureRule` that contains both "FeatureToggleX" and "FeatureToggleX_Details" as elements.

*   **Conceptual Validation Logic (`ValidatorEngine`):**
    1.  The `ValidatorEngine` processes these `conditionalRequired` rules after validating individual elements for their own direct requirements (like `required: true`).
    2.  For each `conditionalRequired` rule associated with a `StructureRule`:
        *   It checks for the presence of the `if_element_exists` element within the current structure's processed children.
        *   If `if_element_has_value` is specified, it checks if the antecedent element's content matches that value.
        *   If the "if" condition is met:
            *   It then checks if the `then_element_is_required` element is present among the structure's children.
            *   If the "then" element is missing, a validation error is reported.
    3.  This requires the `ValidatorEngine` to have access to the state of all sibling elements when validating a structure.

This "basic" conditional logic is feasible but needs careful implementation to correctly resolve element names and their values within the current validation context.

## Application to Dynamic README Scenario

*   **Schema Inheritance/Composition:**
    *   **`MyProjectReadmeStub.yaml` inheriting from a `BaseReadme.yaml`:**
        *   `BaseReadme.yaml` could define common sections like `License` and `Acknowledgments` with basic structure.
        *   `MyProjectReadmeStub.yaml` could `extend: BaseReadme.yaml` and then add project-specific sections like `ProjectOverview`, `QuickStart`, or override the `License` section if needed.
        *   This reduces redundancy if you have multiple projects that share common README elements.
    *   **Frontmatter:** A `BasePage.yaml` could define standard frontmatter fields (e.g., `title: {required: true}`, `draft: {value_type: Boolean}`). `MyProjectReadmeStub.yaml` (if it used frontmatter) could extend this and add `version_added: {value_type: Text}`.

*   **Advanced Validation Rules:**
    *   **`readme_maturity_levels.md`:**
        *   If this document had a more structured format, perhaps for defining specific checks or recommendations:
            *   **Regex:** A field for `check_id` within each recommendation could be validated with a regex: `validations: [{type: pattern, value: "^CHK-[A-Z]+-\d{3}$"}]` to enforce an ID format.
            *   **Enums:** A `recommendation_category` field could use an enum: `validations: [{type: enum, value: ["Content", "Structure", "Metadata", "Presentation"]}]`.
    *   **`MyProjectReadmeStub.yaml` / `StandardProjectREADME.yaml`:**
        *   **Regex:** A `version` field in the frontmatter (if used) could be validated: `validations: [{type: pattern, value: "^\d+\.\d+\.\d+$"}]` for semantic versioning.
        *   **Enums:** A `status` field in frontmatter: `validations: [{type: enum, value: ["Draft", "Review", "Published"]}]`.
        *   **Conditional Logic:**
            *   If the `Installation` section (a `StructureRule`) has an element `Installation.PlatformSpecificInstructionsPresent: {markdown_type: Paragraph, required: false}`.
            *   A conditional rule on the `Installation` StructureRule:
                ```yaml
                # In Installation StructureRule validations:
                # - type: conditionalRequired
                #   value:
                #     if_element_exists: "PlatformSpecificInstructionsPresent" 
                #     then_element_is_required: "PlatformSelector" # Another element in Installation
                #   message: "If platform-specific instructions are noted, a platform selector must be included."
                ```

## Pydantic Model Updates

(Showing key changes or new models. `ValidationRule` from Phase 0 is largely reused for regex/enum.)

```python
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field as PydanticField

# --- ValidationRule (Phase 0, confirmed adequate for regex/enum) ---
class ValidationRule(BaseModel):
    type: Literal[
        "required", "minLength", "maxLength", "pattern", "enum",
        "minCount", "maxCount", "unique", "custom",
        "conditionalRequired" # New type for Phase 1
    ]
    value: Optional[Any] = None
    message: Optional[str] = None
    # case_sensitive_enum: Optional[bool] = None # Could add for enum specific case sensitivity
    # regex_flags: Optional[List[str]] = None # e.g. ["IGNORECASE"] for pattern

# --- Value model for conditionalRequired ---
class ConditionalRequirementValue(BaseModel):
    if_element_exists: Optional[str] = None # Name of an element within the same parent StructureRule
    if_element_has_value: Optional[Any] = None # Check if the if_element_exists has this value
    # if_element_matches_pattern: Optional[str] = None # Future

    then_element_is_required: str # Name of another element that becomes required
    # then_element_must_have_value: Optional[Any] = None # Future

# --- FieldDefinition (Phase 0, largely unchanged, uses ValidationRule) ---
class FieldDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    markdown_type: Literal[
        "Paragraph", "Heading", "List", "ListItem", "CodeBlock", "BlockQuote", "Link", "Image", "Emphasis", "Strong", "Text"
    ]
    required: bool = False
    validations: List[ValidationRule] = PydanticField(default_factory=list)
    fields: Optional[Dict[str, 'StructureRule']] = None # For nested structures within a field (e.g. complex list item)
    language: Optional[str] = None # For CodeBlock markdown_type, to specify expected language

# --- StructureRule (Phase 0, 'validations' list now more powerful) ---
class StructureRule(BaseModel):
    name: str
    description: Optional[str] = None
    entry_marker_type: Literal["Heading", "CustomDelimiter", "List", "ListItem", "Paragraph"]
    entry_marker_properties: Optional[Dict[str, Any]] = None
    elements: Dict[str, Union[FieldDefinition, 'StructureRule']] = PydanticField(default_factory=dict)
    validations: List[ValidationRule] = PydanticField(default_factory=list) # Can now include conditionalRequired
    ordered: bool = False
    element_order: Optional[List[str]] = None
    allow_extra_elements: bool = True

# --- New: Frontmatter Support ---
class FrontmatterFieldDefinition(BaseModel):
    # name is the key in the dictionary 'fields' below
    description: Optional[str] = None
    # For frontmatter, value_type is more abstract than markdown_type
    value_type: Literal["string", "number", "boolean", "list[string]", "list[number]", "object"] # Example types
    required: bool = False
    validations: List[ValidationRule] = PydanticField(default_factory=list) # Can use pattern, enum etc.

class FrontmatterSchema(BaseModel):
    fields: Dict[str, FrontmatterFieldDefinition] = PydanticField(default_factory=dict)
    # allow_extra_fields_in_frontmatter: bool = True # Future

# --- DocModelSchema (Updated for Phase 1) ---
class DocModelSchema(BaseModel):
    schema_name: str
    version: str
    description: Optional[str] = None
    
    extends: Optional[str] = None # Path to a base schema YAML (relative to current file or project root)
    includes: List[str] = PydanticField(default_factory=list) # List of paths to fragment YAMLs

    frontmatter_schema: Optional[FrontmatterSchema] = None # Rules for document frontmatter

    # Structure rules defined directly in this schema or merged from extends/includes
    structure: Dict[str, StructureRule] = PydanticField(default_factory=dict)
    
    # Allow undefined elements globally for this schema, can be overridden by StructureRule.allow_extra_elements
    # This is effectively a default for all StructureRules if not set there.
    # allow_extra_elements_globally: bool = True # Might be better to manage this per StructureRule

# Forward references update
FieldDefinition.update_forward_refs()
StructureRule.update_forward_refs()
```

## ValidatorEngine Updates (Conceptual)

The `ValidatorEngine` from Phase 0 needs to be extended:

1.  **Schema Loading Integration:**
    *   It will receive the *effective* `DocModelSchema` object from the updated `SchemaLoader`, which has already processed any `extends` and `includes` directives and merged them into a single, coherent schema representation. The `ValidatorEngine` itself doesn't need to know about `extends` or `includes` directly; it just works with the final merged schema.

2.  **Frontmatter Validation:**
    *   A new step will be added to validate the document's frontmatter (if present) against the `DocModelSchema.frontmatter_schema`.
    *   This involves parsing the frontmatter (typically YAML) from the document, then for each field defined in `frontmatter_schema.fields`, applying its `required` checks and `validations` (like `pattern` for string fields, `enum` for allowed values).

3.  **Enhanced Field Validation Logic:**
    *   When validating elements based on `FieldDefinition` or `FrontmatterFieldDefinition`:
        *   **Regex:** If a `ValidationRule(type="pattern", value="...")` is present, compile the regex pattern and match it against the field's string content. Report error if no match.
        *   **Enums:** If a `ValidationRule(type="enum", value=[...])` is present, check if the field's content is one of the allowed values. Report error if not. Consider case sensitivity based on an additional flag in `ValidationRule` or a global setting.

4.  **Conditional Logic (`conditionalRequired`) Processing:**
    *   This is the most complex addition. When validating a `StructureRule` (e.g., a document section):
        *   After processing all its defined `elements` for their own direct rules (presence, type, individual validations):
        *   Iterate through any `conditionalRequired` rules in the `StructureRule.validations` list.
        *   For each such rule:
            *   **Identify Antecedent:** Find the element named in `if_element_exists` among the already processed children/elements of the current `StructureRule`.
            *   **Check Condition:**
                *   If `if_element_exists` is specified: check if the antecedent element was actually found.
                *   If `if_element_has_value` is also specified: check if the content of the antecedent element matches this value.
            *   **Check Consequent:** If the "if" condition is true, then find the element named in `then_element_is_required`. If this "then" element was NOT found (or is empty and should not be), then report a validation error using the custom message.
        *   This requires the engine to have a view of all sibling elements and their content/state while processing the parent `StructureRule`.

5.  **Error Reporting:**
    *   Error messages for new validation types (regex, enum, conditional) must be clear and actionable, following NFR3.
    *   Rule IDs for these new checks should be established for noise reduction (NFR4).

The `ValidatorEngine`'s main loop of traversing the document structure (based on the "Internal Structure Map" from Phase 0, Deliverable 6, if that's the input) and matching elements against `StructureRule` and `FieldDefinition` definitions remains similar, but the checks performed for each field/element are expanded.Okay, I have created the new Markdown document for Phase 1, Deliverable 1.

It is saved as: `docs/docmodel_engine/advanced_docmodel_engine.md`

The document covers:
1.  **Reiterated Theme/Goal:** The purpose of advancing the DocModel Engine with schema reuse and more complex validation.
2.  **Technical Implementation Approach:**
    *   **Schema Inheritance/Composition:**
        *   Proposed YAML syntax for `extends` (single inheritance) and `includes` (merging fragments/definitions). A simplified merge strategy for `includes` for Phase 1 is detailed (later includes/definitions override earlier ones).
        *   Schema loading and resolution logic: How `SchemaLoader` recursively loads base schemas, merges properties (child overrides parent for `extends`), and incorporates included definitions. Path resolution and caching are mentioned.
        *   Conflict resolution strategy: Child wins in `extends`; later wins in `includes` or direct definitions.
        *   Pydantic model updates for `DocModelSchema` to include `extends`, `includes`, and a new `frontmatter_schema` section. `FrontmatterSchema` and `FrontmatterFieldDefinition` are introduced.
    *   **Advanced Validation Rules:**
        *   **Regex Matching:** Confirmed that the Phase 0 `ValidationRule(type="pattern")` is suitable. Clarified `ValidatorEngine`'s use of `re.match/search/fullmatch`.
        *   **Enums:** Confirmed that the Phase 0 `ValidationRule(type="enum")` is suitable. Discussed case sensitivity.
        *   **Conditional Logic (Basic "if-then-required"):**
            *   Assessed feasibility, proposing a `conditionalRequired` type in `ValidationRule`.
            *   Defined a `ConditionalRequirementValue` Pydantic model for the `value` of this rule.
            *   Outlined schema representation and conceptual `ValidatorEngine` logic for checking conditions on sibling elements.
3.  **Application to Dynamic README Scenario:**
    *   Illustrated how `MyProjectReadmeStub.yaml` could inherit from a `BaseReadme.yaml`.
    *   Showed how `readme_maturity_levels.md` or `MyProjectReadmeStub.yaml` could use regex for IDs/versions, enums for status/categories, and conditional logic for interdependent fields.
4.  **Pydantic Model Updates:**
    *   Showed updated `DocModelSchema` with `extends`, `includes`, `frontmatter_schema`.
    *   Introduced `FrontmatterSchema` and `FrontmatterFieldDefinition`.
    *   Confirmed `ValidationRule` from Phase 0 is mostly sufficient but added `conditionalRequired` to its `type` literal.
    *   Introduced `ConditionalRequirementValue`.
    *   Minor addition of `language` to `FieldDefinition` for `CodeBlock` type.
5.  **ValidatorEngine Updates (Conceptual):**
    *   Described how it would work with an effective schema from `SchemaLoader`.
    *   Addition of frontmatter validation.
    *   Integration of regex, enum, and the new conditional logic into its validation steps for fields and structures.

The document focuses on evolving the Phase 0 DocModel Engine, providing detailed YAML syntax, Pydantic model changes, and conceptual updates to the validation machinery.
