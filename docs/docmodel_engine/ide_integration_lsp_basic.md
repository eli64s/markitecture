# Essential Integrations: IDE Integration - LSP Basic (Phase 0, Deliverable 4.1)

## Reiterated Theme/Goal

The goal of this deliverable (FR4.1) is to provide basic IDE integration for Markitect by implementing a Language Server Protocol (LSP) server. This will offer users real-time feedback within their development environment, initially focusing on diagnostics (schema violations, code syntax errors) and document synchronization. This enhances the user experience by highlighting issues directly as they edit Markdown documents.

## Technical Implementation Approach

### LSP Server Architecture

**1. Chosen LSP Library:**

*   **`pygls` (Python):** This library will be used for implementing the language server in Python. It's well-maintained, feature-rich, and aligns with Markitect being a Python-based tool. `pygls` handles the LSP message protocol (JSON-RPC) and provides a convenient way to define handlers for various LSP requests.

**2. Key LSP Features to Implement (Phase 0):**

*   **Diagnostics (`textDocument/publishDiagnostics`):**
    *   The server will report errors and warnings identified by Markitect's core validation logic (DocModel Engine for schema violations, and Code Syntax Validator for code snippet errors from Deliverable 3.2).
    *   These will appear in the IDE's "Problems" pane and often as squiggly underlines in the editor.
*   **Document Synchronization (`textDocument/didOpen`, `textDocument/didChange`, `textDocument/didSave`):**
    *   `textDocument/didOpen`: Triggered when a Markdown document is opened in the IDE. The server receives the full document content.
    *   `textDocument/didChange`: Triggered when a document is modified. The server receives incremental changes or the full document content, depending on the client's capabilities and server configuration. For Phase 0, full content sync on change is simpler to manage.
    *   `textDocument/didSave`: Triggered when a document is saved. This can be an additional trigger for validation.

**3. Request Handlers:**

The `pygls` library uses decorators to define handlers for LSP messages.

*   `@server.feature(TEXT_DOCUMENT_DID_OPEN)`
    *   Receives `DidOpenTextDocumentParams` (contains document URI and content).
    *   The server will store this document content in memory, associated with its URI.
    *   It will then trigger a full validation (schema and code syntax) for this document.
*   `@server.feature(TEXT_DOCUMENT_DID_CHANGE)`
    *   Receives `DidChangeTextDocumentParams`. For Phase 0, we'll configure for full content synchronization (`TextDocumentSyncKind.FULL`).
    *   The server updates its in-memory store of the document content.
    *   Triggers a full validation for the changed document.
*   `@server.feature(TEXT_DOCUMENT_DID_SAVE)`
    *   Receives `DidSaveTextDocumentParams`.
    *   Can be an additional trigger for validation, or can be used to trigger actions that only make sense on save (e.g., more expensive checks, though not the focus for Phase 0). For now, it will behave similarly to `didChange`.
*   `@server.feature(INITIALIZE)`
    *   Handles the initial handshake with the LSP client (IDE).
    *   The server declares its capabilities here (e.g., it supports `textDocumentSync` of type `FULL`, and provides diagnostics).
    *   This is also where the server might perform initial setup, like loading the Markitect project configuration (`markitect.yaml`).

### Integration with Markitect Core

**1. Initialization and Configuration:**

*   **Workspace Root:** The LSP server will be aware of the workspace root (the top-level folder opened in the IDE). This is crucial for locating `markitect.yaml` and resolving project-relative paths. `pygls` provides access to this via `server.workspace.root_path`.
*   **Loading `markitect.yaml`:**
    *   On initialization (or when the workspace root is first known), the server will attempt to find and load `markitect.yaml` from the workspace root.
    *   The Markitect configuration loading logic (potentially using Pydantic models like `MarkitectProjectConfig` from Deliverable 3.1) will be reused.
    *   If `markitect.yaml` is not found, the server might operate with default settings or provide a diagnostic message indicating that Markitect features are limited.
*   **Initializing Markitect Services:**
    *   Based on the loaded configuration, the LSP server will instantiate and configure the necessary Markitect services:
        *   `SchemaLoader` and `ValidatorEngine` (from DocModel Engine - Deliverable 1) for schema validation.
        *   `ConsistencyChecker` (for term consistency and link checking - Deliverable 3.1, though diagnostics for these might be Phase 1 for LSP). For Phase 0 LSP, the focus is on DocModel schema and code syntax.
        *   `CodeValidationService` (for code snippet syntax - Deliverable 3.2).
    *   These services will be held as members of the language server instance.
    *   The Markitect core logic will be imported and used as a library within the LSP server process. This is preferred over shelling out to the Markitect CLI for performance.

**2. Managing Document State and Triggering Re-validation:**

*   **In-Memory Document Store:** The LSP server will maintain a dictionary mapping document URIs (as strings) to their current content (as strings). This store is updated by `didOpen` and `didChange` handlers.
*   **Validation Trigger:**
    *   When a document's content is received/updated, a validation task for that document is triggered.
    *   This task will:
        1.  Parse the Markdown content into an AST (using Markitect's `MarkdownParserAdapter`).
        2.  Create a `ParsedDoc` (or similar structure) containing the URI, AST, and project root.
        3.  Invoke the `ValidatorEngine.validate_ast()` method for schema validation.
        4.  Invoke the `CodeValidationService.validate_snippet()` for each code snippet found in the AST.
        5.  Collect all errors from these services.
        6.  Convert these errors into LSP `Diagnostic` objects.
        7.  Publish the diagnostics to the client using `server.publish_diagnostics(doc_uri, diagnostics_list)`.

**3. Asynchronous Operations:**

*   Validation can be time-consuming for large documents or complex schemas. `pygls` supports asynchronous request handling (`async def` handlers).
*   Validation tasks should be run asynchronously to avoid blocking the server from responding to other client requests (like further document changes).
*   A debouncing mechanism might be useful for `textDocument/didChange`: wait a short period (e.g., 500ms) after a change before triggering validation to avoid excessive computation during rapid typing. `pygls` has utilities that can help with this.

### Error Mapping

Markitect's internal error/validation objects (e.g., `ValidationError` from DocModel Engine, `SyntaxErrorDetail` from Code Syntax Validator) need to be mapped to LSP `Diagnostic` objects.

*   **LSP `Diagnostic` structure:**
    *   `range`: A `Range` object (start line, start char, end line, end char) specifying the location of the error in the document. This requires Markitect error objects to provide detailed location information.
        *   Schema validation errors from `ValidatorEngine` need to point to the specific AST node that failed validation, and this node's location in the source Markdown needs to be determined. AST nodes from most parsers (like `mistune` if configured correctly) can provide line/column information.
        *   `SyntaxErrorDetail.error_line_in_snippet` needs to be combined with `CodeSnippet.line_number_start` to get the absolute line in the document.
    *   `message`: The human-readable error message.
    *   `severity`: `DiagnosticSeverity.ERROR`, `DiagnosticSeverity.WARNING`, etc.
    *   `source`: A string identifying the source of the diagnostic (e.g., "Markitect:Schema", "Markitect:PythonSyntax").

*   **Mapping Function (Conceptual):**
    ```python
    from pygls.types import Diagnostic, Range, Position, DiagnosticSeverity

    def map_markitect_error_to_diagnostic(error: Any, doc_uri: str) -> Diagnostic:
        # This function would need to handle different types of Markitect errors
        # and extract location information appropriately.

        start_line, start_char = 0, 0
        end_line, end_char = 0, 1 # Default to a small range at the start if no info
        msg = "Unknown Markitect error"
        severity = DiagnosticSeverity.Error
        source_name = "Markitect"

        if isinstance(error, DocModelValidationError): # Conceptual error from DocModel Engine
            source_name = "Markitect:Schema"
            msg = error.message
            # Location info from error.path_in_document or error.ast_node_location
            # Needs conversion to 0-indexed LSP Range.
            # start_line = error.location.start_line -1
            # ...
        elif isinstance(error, SyntaxErrorDetail): # From Deliverable 3.2
            source_name = f"Markitect:{error.language.capitalize()}Syntax"
            msg = error.message
            # Calculate absolute line number
            abs_error_line = (error.snippet_start_line -1) + (error.error_line_in_snippet -1)
            start_line = abs_error_line
            end_line = abs_error_line
            # TODO: Get character range if available from error.error_column_in_snippet
            # For now, highlight the whole line or a default part of it.
            # end_char = 80 # Highlight a significant portion of the line

        # Placeholder for actual range calculation
        # Range requires 0-indexed lines and characters
        lsp_range = Range(
            start=Position(line=max(0, start_line), character=start_char),
            end=Position(line=max(0, end_line), character=max(start_char + 1, end_char)) # Ensure end > start
        )

        return Diagnostic(range=lsp_range, message=msg, severity=severity, source=source_name)
    ```
    This mapping will be a critical part of the LSP server implementation, requiring careful handling of line and character positions (0-indexed vs 1-indexed, relative vs absolute).

## VS Code Extension (Conceptual Outline)

While the focus is the LSP server, a minimal VS Code extension is needed to consume it.

*   **`package.json`:**
    *   Declares activation events (e.g., `onLanguage:markdown`).
    *   Specifies the main entry point for the extension (e.g., `extension.js`).
    *   Contributes language client configuration (path to the server executable, arguments).
*   **Extension Entry Point (e.g., `extension.ts` or `extension.js`):**
    *   **`activate()` function:**
        *   Locate the Markitect LSP server executable (e.g., a Python script packaged with the extension or requiring user to have Markitect installed and on PATH).
        *   Define `ServerOptions`: command and arguments to start the LSP server.
        *   Define `LanguageClientOptions`: document selector (e.g., `{ language: 'markdown', scheme: 'file' }`), synchronization settings.
        *   Create a new `LanguageClient` instance.
        *   Start the client (`client.start()`). This also starts the server process.
    *   **`deactivate()` function:**
        *   Stop the language client if it's running.

This client-side part is relatively standard for LSP-based extensions.

## Application to Dynamic README Scenario

*   **Editing `readme_maturity_levels.md`:**
    *   Assume `readme_maturity_levels.md` is associated with a DocModel schema (e.g., a "FrameworkDefinitionDocument" archetype as discussed in Deliverable 2).
    *   If a user edits `readme_maturity_levels.md` and violates its schema:
        *   For example, if a required section "LevelCriteria" (defined in the schema) is accidentally deleted from a "Bronze Level" definition.
        *   Upon `didChange` (or `didSave`), the Markitect LSP server re-validates the document against its schema.
        *   The `ValidatorEngine` detects the missing "LevelCriteria".
        *   The error is mapped to an LSP `Diagnostic` object. The `range` of this diagnostic would ideally point to the "Bronze Level" heading or the section where "LevelCriteria" was expected.
        *   The IDE displays this diagnostic, e.g., an error underline on the "Bronze Level" heading and an entry in the "Problems" pane: "Markitect:Schema: Required element 'LevelCriteria' not found in structure 'BronzeLevel'."

*   **Editing `README.stub`:**
    *   Assume `README.stub` is associated with a schema (e.g., `archetype_StandardProjectREADME.yaml`).
    *   **Schema Violations:**
        *   If the user adds a top-level heading `### My Random Section` not defined in the `StandardProjectREADME` schema (and `allow_extra_elements` is false for the root), this would be flagged. The diagnostic would appear on the line with `### My Random Section`.
    *   **Code Snippet Syntax Errors:**
        *   If `README.stub` contains:
            ```markdown
            ```python
            def my_func(
                print("Hello") # SyntaxError: unexpected indent
            ```
            ```
        *   On change/save, the `CodeValidationService` (via `PythonSyntaxValidator`) processes this snippet.
        *   `python -m py_compile` detects the `SyntaxError`.
        *   This is mapped to a `Diagnostic`. The `range` would point to the line `print("Hello")` within the Markdown document.
        *   The IDE shows an error on that line: "Markitect:PythonSyntax: SyntaxError: unexpected indent (or similar message from `py_compile`)".

*   **Validation Target (Phase 0):**
    *   The LSP server in Phase 0 validates the document currently being edited, which is `README.stub` (or any other Markdown file like `readme_maturity_levels.md`).
    *   It does **not** validate the *generated* `README.md` in real-time through the LSP, as the generation step is separate. The validation of the generated `README.md` would typically happen when the `markitect generate` CLI command is run. Providing LSP diagnostics on a generated file that the user isn't directly editing is complex and less useful for immediate feedback.

## Core Function Signatures / Class Definitions (Conceptual - LSP Server specific)

```python
import asyncio
from pygls.server import LanguageServer
from pygls.types import (
    InitializeParams, DidOpenTextDocumentParams, DidChangeTextDocumentParams, DidSaveTextDocumentParams,
    Diagnostic, Range, Position, DiagnosticSeverity, MessageType
)
from pygls.protocol import LanguageServerProtocol
# Assuming Markitect core components are importable
# from markitect.core.config_loader import MarkitectProjectConfig, load_project_config
# from markitect.core.docmodel_engine import ValidatorEngine, SchemaLoader # Simplified
# from markitect.core.syntax_validator import CodeValidationService, CodeSnippet # Simplified
# from markitect.core.markdown_parser import MarkdownParserAdapter # Simplified

# Placeholder for actual Markitect error types
class DocModelValidationError(Exception):
    def __init__(self, message, line=0, col=0, end_line=None, end_col=None):
        self.message = message; self.line = line; self.col = col
        self.end_line = end_line if end_line is not None else line
        self.end_col = end_col if end_col is not None else col + 80 # Default length

class SyntaxErrorDetail(BaseModel): # From Deliverable 3.2
    doc_path: Path
    snippet_start_line: int
    error_line_in_snippet: int
    language: str
    message: str
    # tool_source: str


class MarkitectLanguageServer(LanguageServer):
    # Configuration and Markitect service instances
    # project_config: Optional[MarkitectProjectConfig] = None
    # schema_validator: Optional[ValidatorEngine] = None
    # code_validator: Optional[CodeValidationService] = None
    # markdown_parser: Optional[MarkdownParserAdapter] = None
    # workspace_root: Optional[Path] = None

    # In-memory store for document content
    # document_store: Dict[str, str] = {} # uri -> content

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_config = None
        self.schema_validator = None # Placeholder for actual ValidatorEngine
        self.code_validator = None # Placeholder for actual CodeValidationService
        self.markdown_parser = None # Placeholder for actual MarkdownParserAdapter
        self.workspace_root = None
        self.document_store = {} # uri (str) -> content (str)
        self.debounce_tasks = {} # uri (str) -> asyncio.Task


    async def _load_configuration_and_services(self, params: InitializeParams):
        if params.root_uri:
            self.workspace_root = Path(params.root_uri.replace('file://', ''))
            # try:
            #     self.project_config = load_project_config(self.workspace_root / "markitect.yaml")
            #     # Initialize SchemaLoader, ValidatorEngine, CodeValidationService based on project_config
            #     # self.markdown_parser = MarkdownParserAdapter()
            #     # self.schema_validator = ValidatorEngine(loaded_schema_from_config)
            #     # self.code_validator = CodeValidationService(self.project_config.code_validation_config)
            #     self.show_message("Markitect configuration loaded successfully.", MessageType.Info)
            # except FileNotFoundError:
            #     self.project_config = MarkitectProjectConfig() # Default config
            #     self.show_message("markitect.yaml not found, using default settings.", MessageType.Warning)
            # except Exception as e:
            #     self.project_config = MarkitectProjectConfig() # Default config
            #     self.show_message(f"Error loading markitect.yaml: {e}. Using defaults.", MessageType.Error)
        else:
            self.show_message("Workspace root not provided. Markitect features will be limited.", MessageType.Warning)


    async def _validate_document(self, doc_uri: str):
        content = self.document_store.get(doc_uri)
        if content is None or self.workspace_root is None: # or not self.project_config:
            return

        diagnostics: List[Diagnostic] = []
        doc_path = Path(doc_uri.replace('file://', ''))

        try:
            # 1. Parse Markdown (Conceptual)
            # ast = self.markdown_parser.parse(content)
            # parsed_doc = ParsedDoc(filepath=doc_path, ast=ast, project_root=self.workspace_root)

            # 2. Schema Validation (Conceptual)
            # if self.schema_validator and self.project_config.schema_validation_enabled_for_doc(doc_path):
            #    schema_errors = self.schema_validator.validate_ast(ast, self.project_config.get_schema_for_doc(doc_path))
            #    for error in schema_errors:
            #        diagnostics.append(self._map_schema_error_to_diagnostic(error))

            # 3. Code Syntax Validation (Conceptual)
            # if self.code_validator:
            #    code_snippets = self._extract_code_snippets_from_ast(ast, doc_path, parsed_doc.project_root)
            #    for snippet in code_snippets:
            #        syntax_errors = self.code_validator.validate_snippet(snippet)
            #        for error_detail in syntax_errors:
            #            diagnostics.append(self._map_syntax_error_to_diagnostic(error_detail))
            pass # Actual calls to Markitect core would go here

        except Exception as e:
            self.show_message_log(f"Error during validation of {doc_uri}: {e}", MessageType.Error)
            # Potentially add a generic diagnostic for unexpected errors
            diagnostics.append(Diagnostic(
                range=Range(start=Position(line=0,character=0), end=Position(line=0,character=80)),
                message=f"Unexpected validation error: {e}",
                severity=DiagnosticSeverity.Error,
                source="Markitect:Core"
            ))

        self.publish_diagnostics(doc_uri, diagnostics)

    def _map_schema_error_to_diagnostic(self, error: DocModelValidationError) -> Diagnostic: # Placeholder
        # Convert error.line, error.col etc. to 0-indexed LSP Range
        # Ensure start_line <= end_line and start_char <= end_char if on same line
        line = max(0, error.line -1)
        col = max(0, error.col -1)
        end_line = max(0, error.end_line -1 if error.end_line is not None else line)
        end_col = max(0, error.end_col -1 if error.end_col is not None else col + 1)
        if end_line == line and end_col < col: end_col = col + 1

        return Diagnostic(
            range=Range(start=Position(line=line, character=col), end=Position(line=end_line, character=end_col)),
            message=error.message,
            severity=DiagnosticSeverity.Error, # Or Warning based on error type
            source="Markitect:Schema"
        )

    def _map_syntax_error_to_diagnostic(self, error: SyntaxErrorDetail) -> Diagnostic: # Placeholder
        # Adjust for 0-indexing and combine snippet line with error line
        snippet_start_0idx = error.snippet_start_line - 1
        error_line_in_doc_0idx = snippet_start_0idx + (error.error_line_in_snippet - 1)

        # Ensure line numbers are non-negative
        actual_line = max(0, error_line_in_doc_0idx)

        return Diagnostic(
            range=Range(
                start=Position(line=actual_line, character=0), # TODO: Use column info if available
                end=Position(line=actual_line, character=80) # Highlight line
            ),
            message=error.message,
            severity=DiagnosticSeverity.Error,
            source=f"Markitect:{error.language.capitalize()}Syntax"
        )

    async def _debounced_validate(self, doc_uri: str):
        if doc_uri in self.debounce_tasks:
            self.debounce_tasks[doc_uri].cancel()

        async def validation_coro():
            await asyncio.sleep(0.5) # 500ms debounce
            await self._validate_document(doc_uri)

        self.debounce_tasks[doc_uri] = asyncio.create_task(validation_coro())


# LSP method handlers using Pygls decorators would be part of this class:
# @server.feature(INITIALIZE)
# async def initialize(self, params: InitializeParams):
#     await self._load_configuration_and_services(params)
#     # Define server capabilities (e.g., TextDocumentSyncKind.FULL)

# @server.feature(TEXT_DOCUMENT_DID_OPEN)
# async def did_open(self, params: DidOpenTextDocumentParams):
#     self.document_store[params.text_document.uri] = params.text_document.text
#     await self._validate_document(params.text_document.uri) # Initial validation

# @server.feature(TEXT_DOCUMENT_DID_CHANGE)
# async def did_change(self, params: DidChangeTextDocumentParams):
#     # Assuming TextDocumentSyncKind.FULL, content is the full new text
#     self.document_store[params.text_document.uri] = params.content_changes[0].text
#     await self._debounced_validate(params.text_document.uri)

# @server.feature(TEXT_DOCUMENT_DID_SAVE)
# async def did_save(self, params: DidSaveTextDocumentParams):
#     # Can simply re-trigger validation, or specific on-save actions
#     # For Phase 0, treat like did_change or ensure validation happens
#     await self._debounced_validate(params.text_document.uri)

```

## Performance Considerations (NFR1)

*   **Asynchronous Operations:** Using `async/await` for handlers and validation tasks is crucial, as provided by `pygls` and `asyncio`.
*   **Debouncing:** For `textDocument/didChange`, debouncing validation calls prevents excessive work during rapid typing.
*   **Efficient Core Logic:** The performance of Markitect's core validation (schema checking, AST parsing, code validation) directly impacts LSP responsiveness. These should be optimized as much as reasonably possible.
    *   AST parsing can be intensive. Caching ASTs if they haven't changed might be complex with incremental updates but could be considered for unchanged includes.
    *   External tool calls for code syntax validation add overhead (process creation, temp files). Using internal libraries (like for YAML/JSON) is faster. For other languages, this is a trade-off for robustness.
*   **Full vs. Incremental Sync:** Phase 0 uses full document sync on change for simplicity. Incremental sync can be more performant for large documents but adds complexity to updating the document state and applying validation. This can be a future optimization.
*   **Configuration Loading:** `markitect.yaml` and associated schemas/glossaries should ideally be loaded once at server start or when the config file changes, not per validation request. File watching for `markitect.yaml` could trigger a reload.

This approach details the creation of a basic LSP server for Markitect, focusing on diagnostics and document synchronization for Phase 0. It outlines the integration with existing Markitect core logic and provides a conceptual foundation for a VS Code extension.Okay, I will create the new Markdown document `docs/docmodel_engine/ide_integration_lsp_basic.md` for Phase 0, Deliverable 4.1.
