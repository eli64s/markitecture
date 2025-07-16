# Core Non-Functional Requirements (Phase 0, Deliverable 5)

This document outlines the strategies and considerations for addressing key non-functional requirements (NFRs) in Markitect's Minimum Viable Product (MVP) / Phase 0.

---

## NFR1: Performance

*   **NFR Statement:** Markitect should provide responsive feedback for both CLI and LSP interactions, ensuring it does not unduly hinder the user's workflow.
*   **Goal for Phase 0:**
    *   CLI: For small to medium-sized projects (e.g., up to 50-100 Markdown files, each up to a few hundred lines), validation should complete within a few seconds.
    *   LSP: Diagnostics for a single, average-sized Markdown file (e.g., up to 500 lines) should appear within 1-2 seconds after a pause in typing or on save.
    *   Focus is on "reasonable" performance for common use cases, not exhaustive optimization for extreme edge cases.
*   **Strategies/Considerations:**
    1.  **Efficient Core Logic:**
        *   **Schema Loading:** Parse YAML/JSON configuration files efficiently. Pydantic model validation is generally fast but schemas should not be excessively deep or complex for Phase 0 use cases. Cache loaded schemas if they are referenced by multiple documents.
        *   **Markdown Parsing:** Leverage efficient underlying Markdown parsing libraries (e.g., `mistune` in C, or `markdown-it-py` which is also fast). Parse a document once per validation cycle.
        *   **AST Traversal:** Implement non-recursive or bounded-depth recursive traversals where possible to avoid stack overflows on deeply nested ASTs (though less common in typical Markdown).
        *   **Validation Rules:** Prioritize efficient algorithms for common validation rules. For example, regex matching for `pattern` rules should use compiled regexes. Term lookups in `TermBank` should use efficient data structures (e.g., hash maps, Aho-Corasick for many terms if scaling becomes an issue later).
    2.  **LSP Specifics:**
        *   **Asynchronous Operations:** Utilize `async/await` in `pygls` for all I/O-bound and potentially long-running tasks (validation) to keep the server responsive.
        *   **Debouncing:** Implement debouncing for `textDocument/didChange` events to avoid re-validating on every keystroke. A delay of 300-500ms is typical.
        *   **Full Document Sync:** For Phase 0, use `TextDocumentSyncKind.Full`. While less optimal than incremental sync for very large files, it significantly simplifies state management and validation logic.
    3.  **CLI Specifics:**
        *   **File Discovery:** Use efficient globbing and path manipulation.
        *   **Parallelism (Future):** For Phase 0, sequential processing of files is acceptable. File-level parallelization for validation could be a future optimization if CLI performance on many files becomes a bottleneck.
    4.  **Avoiding Unnecessary Re-computation:**
        *   LSP: Only re-validate the document that changed, not the entire project (unless inter-document dependencies are explicitly being checked, which is minimal for Phase 0 diagnostics).
        *   CLI: Processes each file as needed.
    5.  **External Tool Calls (Code Syntax Validation):**
        *   Subprocess creation has overhead. For Phase 0, this is accepted for the robustness of using mature tools.
        *   Internal parsers/linters (like for YAML, JSON) will be faster than shelling out.
    6.  **Profiling and Benchmarking (Early Thoughts):**
        *   Identify key performance-sensitive operations (e.g., parsing a large Markdown file, validating a document against a complex schema, checking a document with many code snippets).
        *   Use Python's `cProfile` or `timeit` for basic benchmarking of critical functions during development.
        *   Establish baseline performance metrics for a small, representative set of test documents and configurations.
*   **Application to Dynamic README Scenario (Illustrative):**
    *   **`readme_maturity_levels.md` (RML) & `README.stub` Validation:**
        *   LSP: When editing `README.stub`, if it's a 200-line file, diagnostics (schema violations, code errors in examples) should appear quickly after typing stops.
        *   CLI: Running `markitect validate` on a project containing RML, `README.stub`, and a few other typical Markdown files should complete swiftly.
        *   Loading the schemas for RML and `README.stub` should be fast.
        *   Parsing these documents and validating their structure and any embedded code snippets should not introduce noticeable lag.

---

## NFR2: Configuration

*   **NFR Statement:** Markitect's configuration should be clear, discoverable, and easy for users to manage.
*   **Goal for Phase 0:**
    *   Provide a single, primary configuration file (`markitect.yaml`).
    *   Configuration options for Phase 0 features (schema selection, context-awareness rules, code validation settings, basic noise reduction) should be intuitive.
    *   Implement basic discovery for `markitect.yaml`.
    *   Provide clear error messages for invalid configuration syntax or values.
*   **Strategies/Considerations:**
    1.  **Configuration File Format:**
        *   **`markitect.yaml`:** YAML is chosen for its human-readability and ability to represent hierarchical data well.
        *   **`pyproject.toml` (Consideration):** While `pyproject.toml` (under `[tool.markitect]`) is common for Python tools, a standalone `markitect.yaml` might be simpler for non-Python users or projects where `pyproject.toml` is already complex. For Phase 0, `markitect.yaml` is primary. Integration with `pyproject.toml` can be an enhancement.
    2.  **Simplicity and Clarity:**
        *   Group related configurations logically (e.g., `docmodel_validation`, `consistency_checks`, `code_syntax_validation`).
        *   Use descriptive key names.
        *   Provide sensible defaults for most options, allowing users to configure only what they need to change.
        *   Ensure boolean flags are clear (e.g., `enabled: true/false`).
    3.  **Discoverability of Configuration:**
        *   CLI: Search for `markitect.yaml` in the current directory, then parent directories up to the project root (e.g., detected by `.git` or filesystem root). The `--project-root` option can override this.
        *   LSP: Expect `markitect.yaml` in the workspace root provided by the client.
    4.  **Error Handling:**
        *   Use Pydantic models to define the structure of `markitect.yaml`. This provides automatic validation of data types, required fields, and enum choices when loading the configuration.
        *   Report clear error messages if `markitect.yaml` has syntax errors (YAML parsing errors) or validation errors against the Pydantic models (e.g., "Error in markitect.yaml: field 'consistency_checks.term_consistency.default_case_sensitive' must be a boolean").
    5.  **Documentation:** Clearly document all configuration options, their purpose, allowed values, and defaults.
*   **Application to Dynamic README Scenario (Illustrative):**
    *   The `markitect.yaml` file is central to defining the dynamic README setup. It specifies:
        *   Which schema applies to `README.stub` (e.g., `MyProjectReadmeStub.yaml`).
        *   Which schema applies to `readme_maturity_levels.md`.
        *   Paths to glossaries for term consistency between these files.
        *   Settings for validating code snippets within both documents.
    *   A user should find it straightforward to set up these relationships in `markitect.yaml`.

*   **Consolidated `markitect.yaml` Conceptual Example (Phase 0):**

    ```yaml
    # markitect.yaml (Phase 0 Example)
    project_name: "MyAwesomeProject"
    # project_root is implicitly the directory containing markitect.yaml,
    # or can be overridden by CLI --project-root.
    # All relative paths below are resolved against this project_root.

    # --- 1. DocModel Engine Configuration (Deliverable 1 & 2) ---
    docmodel_engine:
      # Defines named schemas that can be referenced elsewhere.
      # Key is a schema ID/name used in document_schema_map or as a default.
      schemas:
        "StandardREADME": # User-defined name for this schema configuration
          path: "docs/schemas/archetype_StandardProjectREADME.yaml"
          # description: "Standard project README archetype." # Optional
        "FrameworkDefinition":
          path: "docs/schemas/archetype_FrameworkDefinitionDocument.yaml" # Conceptual
        "APIDoc":
          path: "docs/schemas/archetype_APIEndpointDoc.yaml"

      # Maps specific documents or glob patterns to a schema ID defined above.
      # More specific patterns override general ones (implementation detail).
      document_schema_map:
        "README.md": "StandardREADME" # Or README.stub if that's the source
        "docs/api/**/*.md": "APIDoc"
        "design/frameworks/*.md": "FrameworkDefinition"

      # Default schema to use if a document isn't covered by the map.
      # Can be a schema ID from 'schemas' or a direct path.
      # default_schema: "StandardREADME"
      # Or: default_schema_path: "path/to/some_default_schema.yaml"

    # --- 2. Context-Awareness: Consistency (Deliverable 3.1) ---
    consistency_checks:
      # Global scope for all consistency checks unless overridden per check type.
      # Globs are relative to project_root.
      scope:
        include:
          - "**/*.md" # Process all Markdown files by default
        exclude:
          - "node_modules/"
          - "vendor/"
          - "docs/archive/"
          - "**/draft_*.md"

      term_consistency:
        enabled: true
        default_case_sensitive: false
        enforce_canonical_form: false # If true, flags approved_alternatives if not identical to canonical
        glossaries: # List of paths to glossary files
          - "docs/glossary/project_terms.yaml"
          # - "shared/company_terms.json" # JSON could be supported later
        defined_terms: # Inline term definitions. Key is a unique slug/ID.
          "k8s-global":
            canonical_form: "Kubernetes"
            approved_alternatives: ["K8s"]
            # case_sensitive not set, uses default_case_sensitive

      link_checking:
        enabled: true
        # check_external_links_live: false # Phase 0: no live checks, only format
        # allowed_external_schemes: ["http", "https", "mailto"] # Optional

    # --- 3. Context-Awareness: Code Syntax Validation (Deliverable 3.2) ---
    code_syntax_validation:
      enabled: true
      on_missing_tool: "warn" # "error", "warn", "ignore"
      languages:
        python:
          enabled: true
          # executable_path: "/usr/bin/python3" # Optional, uses 'python' from PATH by default
        javascript:
          enabled: true
          # executable_path: "/usr/local/bin/node"
        bash:
          enabled: true
        yaml:
          enabled: true # Uses internal PyYAML
        json:
          enabled: true # Uses internal json.loads

    # --- 4. Noise Reduction (NFR4 - Basic) ---
    noise_reduction:
      # Globally disable specific rule IDs from any checker.
      # Rule IDs would need to be documented (e.g., "Schema:MissingRequiredElement", "Syntax:PythonIndentation")
      disable_rules_global:
        # - "Schema:MyCustomRuleIfItWereTooNoisy"
        # - "TermConsistency:SomeTermSlug" # To ignore a specific term everywhere
        pass # No rules disabled globally by default

      # Per-path overrides for disabled rules or specific settings
      overrides:
        - paths: # List of glob patterns
            - "drafts/**/*.md"
            - "legacy_docs/README.md"
          disable_rules: # Disable these rules only for files matching 'paths'
            - "Schema:*" # Disable all schema checks for these files
            - "CodeSyntax:*" # Disable all code syntax checks
        - paths:
            - "README.stub"
          # Example: If a specific schema rule is too noisy for README.stub
          # disable_rules:
          #   - "Schema:StandardREADME.Installation.Prerequisites.required" # Hypothetical rule ID

    # LSP specific settings (if any needed beyond client-side config)
    # language_server:
    #   debounce_delay_ms: 500
    ```

---

## NFR3: Actionability

*   **NFR Statement:** Error messages and validation feedback must be clear, concise, and provide enough information for the user to easily locate and understand the issue.
*   **Goal for Phase 0:**
    *   All error messages should be human-readable and directly point to the problem.
    *   Error reports must include:
        *   File path.
        *   Line number (1-indexed).
        *   Column number (1-indexed, where applicable and available from parsers/tools).
        *   A descriptive message.
        *   The source/type of the error (e.g., Schema, PythonSyntax, Link).
    *   Error messages may suggest the expected format or a potential fix, but auto-fixing is not part of Phase 0.
*   **Strategies/Considerations:**
    1.  **Clarity and Conciseness:**
        *   Avoid jargon where possible or explain it.
        *   Messages should state what was found vs. what was expected.
        *   Example: Instead of "Term invalid", use "Term 'Kubernates' is not an approved variant. Did you mean 'Kubernetes'?"
    2.  **Precise Location Information:**
        *   **Schema Violations:** Leverage line/column information from the Markdown AST parser for the AST node that failed validation.
        *   **Link Errors:** Report the line/column of the `[link text](destination)` Markdown tag.
        *   **Term Inconsistencies:** Report the line/column where the problematic term usage occurs.
        *   **Code Syntax Errors:** Map line/column numbers from the linter (relative to the snippet) back to absolute line/column numbers in the Markdown document. This requires knowing the starting line of the code snippet.
    3.  **Source Identification:** Clearly prefix or categorize errors (e.g., `[Schema]`, `[PythonSyntax]`, `[LinkCheck]`, `[TermCheck]`) so users understand the nature of the error. Rule IDs, if developed, can also be part of this.
    4.  **Suggesting Fixes (Informative):**
        *   While auto-fix is out of scope for Phase 0, messages can guide the user.
        *   Schema: "Missing required element 'SetupInstructions'. Expected after 'InstallationOverview'."
        *   Terms: "Term 'DocModelEngine' (found) does not match canonical form 'DocModel Engine' (case-sensitive)." (If `enforce_canonical_form` and `case_sensitive` are true).
        *   Links: "Internal link './docs/CONTRIB.md' not found. Did you mean './docs/CONTRIBUTING.md'?" (This level of suggestion is advanced; Phase 0 might just say "not found").
    5.  **Consistency in Error Format:** Maintain a relatively uniform structure for error messages across different validation types for better UX in CLI and LSP.
*   **Application to Dynamic README Scenario (Illustrative):**
    *   **Schema error in `README.stub`:**
        *   "FILE: README.stub\n  L10 C1 [ERROR] [Markitect:Schema] Element 'Introduction': Missing required child element 'ProjectSummary'."
    *   **Code syntax error in `README.stub`:**
        *   "FILE: README.stub\n  L25 C5 [ERROR] [Markitect:PythonSyntax] SyntaxError: invalid syntax (in snippet starting L22, line 3 within snippet)."
    *   **Link error in `readme_maturity_levels.md`:**
        *   "FILE: readme_maturity_levels.md\n  L50 C10 [ERROR] [Markitect:LinkCheck] Internal link '/references/style_guide.md' points to a missing file."
    *   **Term error (if `enforce_canonical_form` was true) in `README.stub`:**
        *   "FILE: README.stub\n  L5 C1 [ERROR] [Markitect:TermCheck] Term 'docmodel engine' does not match canonical form 'DocModel Engine' (configured as case-insensitive but canonical form preferred)." (This assumes `enforce_canonical_form` is true; otherwise, if 'docmodel engine' is an approved alternative, it's fine).

---

## NFR4: Noise Reduction

*   **NFR Statement:** Users should be able to manage the "noise" from validation, focusing on relevant issues by ignoring specific rules or files/sections where checks are not applicable or desired.
*   **Goal for Phase 0:**
    *   Provide basic mechanisms to disable specific rule IDs globally or for specified file paths/patterns via `markitect.yaml`.
    *   Ensure default rule sets are generally high-signal and minimally noisy for common use cases.
    *   Inline comment-based ignoring is **out of scope for Phase 0** due to added parsing complexity, but the need is acknowledged.
*   **Strategies/Considerations:**
    1.  **High-Signal Default Rules:**
        *   Focus default schema rules (in archetypes) and consistency checks on unambiguous errors and strong best practices.
        *   Avoid overly pedantic or stylistic rules in the default set for Phase 0.
    2.  **Configuration-Based Ignoring:**
        *   **Global Disable:** In `markitect.yaml`, allow a list of rule IDs to be disabled globally.
            *   `noise_reduction.disable_rules_global: ["Schema:SomeRuleID", "TermConsistency:MyTermSlug"]`
            *   Requires a system of identifiable and documented Rule IDs (e.g., `Schema:MissingRequiredElement`, `Syntax:Python:IndentationError`, `Term:MyTermSlug.CaseSensitive`).
        *   **Per-Path Disable:** Allow disabling rule IDs for specific files or glob patterns.
            *   `noise_reduction.overrides:` (as shown in the NFR2 `markitect.yaml` example). This allows disabling rules like `Schema:*` or `CodeSyntax:*` for specific paths.
    3.  **Rule IDs:**
        *   Develop a consistent and documented scheme for rule identifiers.
        *   Examples:
            *   Schema validation: `Schema:<SchemaName>.<PathToElement>.<ValidationType>` (e.g., `Schema:StandardREADME.Introduction.ProjectPurpose.minLength`) or simpler like `Schema:RequiredElement`.
            *   Term consistency: `Term:<TermCanonicalFormOrSlug>.<CheckType>` (e.g., `Term:Kubernetes.CanonicalForm`).
            *   Link checking: `Link:InternalNotFound`, `Link:ExternalFormat`.
            *   Code syntax: `Syntax:<Language>.<LinterRuleID>` (e.g., `Syntax:Python.E501` if using a linter that provides such IDs, or generic like `Syntax:Python.GenericError`).
        *   For Phase 0, rule IDs might be more coarse-grained (e.g., "Schema:Required", "Syntax:Python").
    4.  **Inline Comments (Future):**
        *   Acknowledge that users often want fine-grained control like `<!-- markitect-ignore-next-line Schema:RequiredElement -->` or `# markitect-ignore CodeSyntax:Python`.
        *   This requires the Markdown parser and subsequent validation steps to be aware of these comments, adding complexity. Defer to a later phase.
    5.  **Severity Levels (Future for Configuration):**
        *   While diagnostics have severity, Phase 0 won't focus on users re-configuring rule severity (e.g., changing a default "error" to a "warning"). This can be a later enhancement.
*   **Application to Dynamic README Scenario (Illustrative):**
    *   A user is working on an early draft of `README.stub` and finds a specific schema rule from `MyProjectReadmeStub.yaml` (e.g., requiring a "DetailedUsage" section) too noisy for the current draft stage.
    *   They can configure `markitect.yaml` to disable this specific check for `README.stub`:
        ```yaml
        # In markitect.yaml
        noise_reduction:
          overrides:
            - paths: ["README.stub"]
              disable_rules:
                # Assuming a rule ID like "Schema:MyProjectReadmeStub.DetailedUsage.Required"
                - "Schema:MyProjectReadmeStub.DetailedUsage.Required"
        ```
    *   If a globally defined term (e.g., "LegacySystem") is correctly used in an archived document section but Markitect flags it (e.g., because `enforce_canonical_form` is true and "LegacySystem" is an alternative), the user could disable that specific term check for that archived path.

---

Addressing these NFRs thoughtfully in Phase 0 will contribute significantly to Markitect's usability, reliability, and adoption. The focus is on robust fundamentals and providing users with necessary controls without overcomplicating the initial MVP.Okay, I have created the new Markdown document for Phase 0, Deliverable 5.

It is saved as: `docs/docmodel_engine/non_functional_requirements_phase0.md`

The document covers the four specified Non-Functional Requirements (NFR1-NFR4):

For each NFR, it includes:
*   **NFR Statement**
*   **Goal for Phase 0:** Specific, measurable targets for the MVP.
*   **Strategies/Considerations:** Detailed approaches and design thoughts for achieving the Phase 0 goals.
*   **Application to Dynamic README Scenario (Illustrative):** Concrete examples of how each NFR applies to the core use case involving `readme_maturity_levels.md` and `README.stub`.

Additionally, for **NFR2 Configuration**, a comprehensive conceptual example of `markitect.yaml` is provided, consolidating settings from previous deliverables (DocModel loading, context-awareness rules, syntax checking options) and incorporating the new NFR-related configurations like noise reduction.

The content focuses on defining the approach and philosophy for these NFRs in Phase 0, ensuring Markitect starts with a solid foundation in performance, configurability, actionability of feedback, and noise reduction.
