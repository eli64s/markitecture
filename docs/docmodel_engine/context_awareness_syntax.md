# Basic Context-Awareness: Code-Awareness - Syntax Validation (Phase 0, Deliverable 3.2)

## Reiterated Theme/Goal

The goal of this deliverable (FR2.2) is to introduce basic syntax validation for code snippets embedded within Markdown documents. This enhances the accuracy of technical documentation by catching rudimentary syntax errors in examples, configurations, and scripts directly within the documentation files. For Phase 0, the focus is on leveraging existing external tools for a core set of common languages, rather than building an in-process parser.

## Technical Implementation Approach

### 1. Code Snippet Extraction

*   **Identification:** Code snippets are extracted from fenced code blocks in Markdown. The Markdown parser (e.g., `mistune`, `commonmark-py`) will identify these blocks. A typical AST node for a fenced code block provides the code content and an "info string" (language identifier).
*   **Data Structure:** A `CodeSnippet` data class will store the extracted information:
    ```python
    from typing import Optional, List
    from pathlib import Path
    from pydantic import BaseModel

    class CodeSnippet(BaseModel):
        content: str
        language: Optional[str] # e.g., "python", "javascript"
        doc_path: Path # Path to the document containing the snippet
        line_number_start: Optional[int] # Line where the snippet begins in the Markdown
        # column_number_start: Optional[int] # Column, if available
    ```

### 2. Language Identification

*   **From Info String:** The language is primarily determined from the info string following the opening fence (e.g., ` ```python ` identifies "python").
*   **Normalization:** The extracted language identifier (e.g., "py", "Python", "python3") should be normalized to a canonical form (e.g., "python") to map to available validators. A predefined mapping can be used:
    *   `{"py", "python", "python3"}` -> `"python"`
    *   `{"js", "javascript"}` -> `"javascript"`
    *   `{"sh", "bash", "shell"}` -> `"bash"`
    *   `{"yaml", "yml"}` -> `"yaml"`
    *   `{"json"}` -> `"json"`
*   **Unsupported/Unspecified Language:** If the language is not specified or the normalized language is not supported by any configured validator, the snippet will be skipped for syntax validation. This should be logged or reported appropriately (e.g., "Skipping syntax check for snippet at ... due to unspecified or unsupported language: ...").

### 3. Syntax Validation Strategy: External Tools Wrapper

For Phase 0, the strategy will be to wrap existing, widely-used external linters or compilers. This approach is generally robust and leverages mature tools.

*   **Mechanism:**
    1.  The `SyntaxValidator` component will receive a `CodeSnippet`.
    2.  Based on the snippet's language, it will select the appropriate external tool (e.g., `python -m py_compile` for Python).
    3.  The code snippet's content will be written to a temporary file. This is often necessary because many command-line tools operate on files.
    4.  The external tool is invoked as a subprocess (e.g., using `subprocess.run()`), targeting the temporary file.
    5.  The output (stdout, stderr) and exit code of the tool are captured.
    6.  The captured output is parsed to extract meaningful error messages, line numbers (relative to the snippet), and severity.
    7.  The temporary file is deleted.

*   **Error Capturing and Normalization:**
    *   Each validator implementation (e.g., `PythonSyntaxValidator`) will be responsible for parsing the specific output format of its corresponding tool.
    *   Error messages, line numbers (which need to be adjusted to be relative to the start of the snippet in the Markdown, if the tool reports them relative to the temp file), and column numbers will be standardized into a `SyntaxErrorDetail` model.

*   **Supported Languages & Tools (Initial Set for Phase 0):**
    *   **Python:** `python -m py_compile` (checks for basic syntax errors). `flake8` could be an option if available, as it provides more, but `py_compile` is part of the standard library.
    *   **JavaScript:** `node -c` (check syntax). `eslint --fix-dry-run` (or similar) could be used if available, but `node -c` is simpler for basic syntax.
    *   **Bash:** `bash -n` (no-execute, checks for syntax errors).
    *   **YAML:** A Python library like `PyYAML` (e.g., `yaml.safe_load()`) can be used internally to parse the YAML content. This is not strictly an "external tool" but leverages a library.
    *   **JSON:** Python's `json.loads()` can be used internally.

### 4. Configuration (`markitect.yaml`)

Configuration options will allow users to enable/disable the feature, manage external tool paths, and specify language-specific settings.

```yaml
# markitect.yaml (within consistency_checks or a dedicated code_validation section)

consistency_checks: # Or a new top-level key like 'code_validation'
  # ... other consistency checks ...

  code_syntax_validation:
    enabled: true
    # Global setting for how to handle missing external tools
    # "error": Fail if a configured tool for a language is not found.
    # "warn": Warn and skip validation for that language.
    # "ignore": Silently skip.
    on_missing_tool: "warn" # Default to "warn"

    languages:
      python:
        enabled: true
        # method: "py_compile" # Default, uses 'python -m py_compile'
        # method: "flake8" # Alternative, if user prefers and has it installed
        # executable_path: "/usr/local/bin/python3.9" # Optional: path to specific python interpreter
        # linter_path: "/path/to/flake8" # Optional: if 'flake8' method and not on PATH

      javascript:
        enabled: true
        # method: "node_check" # Default, uses 'node -c'
        # executable_path: "/path/to/node" # Optional
        # linter_path: "/path/to/eslint" # If an eslint method were supported

      bash:
        enabled: true
        # method: "bash_check" # Default, uses 'bash -n'
        # executable_path: "/bin/bash" # Optional

      yaml:
        enabled: true # Uses internal PyYAML library by default
        # method: "pyyaml" # Default

      json:
        enabled: true # Uses internal json library by default
        # method: "internal" # Default

      # Configuration for a currently unsupported language (Markitect would ignore or warn)
      # rust:
      #   enabled: true
      #   # method: "cargo_check" # User might hope for this
      #   # linter_path: "/path/to/cargo"
```

### 5. Error Reporting

*   Syntax errors will be reported with:
    *   Path to the Markdown document.
    *   Line number where the code snippet begins in the Markdown document.
    *   Line number of the error *within* the code snippet (as reported by the linter, adjusted).
    *   The error message from the linter.
    *   The language of the snippet.

*   A `SyntaxErrorDetail` Pydantic model can structure this:
    ```python
    class SyntaxErrorDetail(BaseModel):
        doc_path: Path
        snippet_start_line: int # Line in Markdown where snippet starts
        error_line_in_snippet: int # Line number of error relative to snippet start
        # error_column_in_snippet: Optional[int] = None
        language: str
        message: str
        tool_source: str # e.g., "py_compile", "bash -n"
    ```

### 6. Application to Dynamic README Scenario

*   **`README.stub` / `README.md`:**
    *   If `README.stub` contains example Python usage like:
        ```python
        # In README.stub
        '''markdown
        Here's how to use it:
        ```python
        import my_project
        result = my_project.do_something(x, y) # Potential error if x,y not defined
        print(result)
        ```
        '''
        The `PythonSyntaxValidator` would run `python -m py_compile` on this snippet. `py_compile` would likely catch basic syntax errors (e.g., mismatched parentheses) but not undefined variables like `x` and `y` as that's a runtime/semantic error. For Phase 0, this is acceptable.
    *   Shell command examples:
        ```markdown
        ```bash
        # Install the project
        pip install .
        # Run it
        my_project --input data.csv
        ```
        The `BashSyntaxValidator` (`bash -n`) would check if these are syntactically valid bash commands (e.g., no unclosed quotes).

*   **`readme_maturity_levels.md`:**
    *   If this document contains examples of configuration (e.g., YAML snippets for `markitect.yaml` itself, or JSON examples), these would be validated by the respective YAML/JSON validators.
        ```markdown
        ```yaml
        # Example markitect.yaml snippet
        consistency_checks:
          scope:
            include: ["docs/*.md"]
          # missing_colon_after_scope # This would be a YAML syntax error
        ```
        The YAML validator (using `PyYAML`) would catch the `missing_colon_after_scope` error.

*   **Validating `update_readme.py` (or other project scripts):**
    *   While the primary goal is validating snippets *in Markdown*, the configuration could potentially be extended to point to standalone script files for validation.
    *   For Phase 0, this is likely out of scope for the *code snippet validation feature*, which focuses on embedded code. Validating entire project source files is standard practice for CI systems using linters directly. However, if `markitect` were to evolve into a more general project quality tool, this could be a future direction. The current focus remains on documentation accuracy.

### 7. Core Function Signatures / Class Definitions (Conceptual)

```python
from abc import ABC, abstractmethod
import subprocess
import tempfile

# (CodeSnippet, SyntaxErrorDetail Pydantic models as defined above)

class SyntaxValidator(ABC):
    """Abstract base class for language-specific syntax validators."""

    language_aliases: List[str] # e.g., ["python", "py"]
    default_executable: Optional[str] = None # e.g., "python"

    def __init__(self, executable_path: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        self.executable = executable_path or self.default_executable
        self.config = config or {}

    @abstractmethod
    def validate(self, snippet: CodeSnippet) -> List[SyntaxErrorDetail]:
        """Validates a code snippet and returns a list of syntax errors."""
        pass

    def _run_external_tool(self, command_args: List[str], code_content: str) -> Tuple[int, str, str]:
        """Helper to run an external tool with code content in a temporary file."""
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=self._get_temp_suffix()) as tmp_file:
                tmp_file.write(code_content)
                tmp_file_path = tmp_file.name

            # Ensure command_args uses the tmp_file_path correctly
            full_command = [arg.replace("{tmp_file}", tmp_file_path) for arg in command_args]

            process = subprocess.run(full_command, capture_output=True, text=True, check=False)
            return process.returncode, process.stdout, process.stderr
        finally:
            if tmp_file_path:
                Path(tmp_file_path).unlink(missing_ok=True)

    def _get_temp_suffix(self) -> str:
        # Override in subclasses for language-specific file extensions if needed by tools
        return ".tmp"


class PythonSyntaxValidator(SyntaxValidator):
    language_aliases = ["python", "py", "python3"]
    default_executable = "python" # Assumes 'python' is on PATH

    def _get_temp_suffix(self) -> str:
        return ".py"

    def validate(self, snippet: CodeSnippet) -> List[SyntaxErrorDetail]:
        errors: List[SyntaxErrorDetail] = []
        if not self.executable:
            # errors.append(SyntaxErrorDetail(..., message="Python executable not configured/found."))
            # This case handled by on_missing_tool at a higher level.
            return errors # Should not proceed if executable is missing.

        # Method 1: py_compile
        # Command: [self.executable, "-m", "py_compile", "{tmp_file}"]
        # Method 2: flake8 (if configured)
        # command_template = self.config.get("command_template", "{executable} -m py_compile {tmp_file}")

        # Assuming py_compile for Phase 0 simplicity
        command_args = [self.executable, "-m", "py_compile", "{tmp_file}"]

        returncode, stdout, stderr = self._run_external_tool(command_args, snippet.content)

        if returncode != 0:
            # Parse stderr for error details. py_compile output format:
            # Sorry: IndentationError: unexpected indent (prog.py, line 3)
            # Or: File "{tmp_file}", line X SyntaxError: ...
            # This parsing logic needs to be robust.
            # Example simplified parsing:
            for line in stderr.splitlines():
                # Add regex parsing here to extract line_in_snippet, message
                # error_line_in_snippet = ...
                # message = ...
                # errors.append(SyntaxErrorDetail(
                #     doc_path=snippet.doc_path,
                #     snippet_start_line=snippet.line_number_start,
                #     error_line_in_snippet=error_line_in_snippet, # Adjusted
                #     language=snippet.language,
                #     message=message,
                #     tool_source=f"{self.executable} -m py_compile"
                # ))
                # For now, just dump the error if parsing is complex
                errors.append(SyntaxErrorDetail(
                    doc_path=snippet.doc_path,
                    snippet_start_line=snippet.line_number_start or 0,
                    error_line_in_snippet=1, # Placeholder - needs parsing
                    language=snippet.language or "python",
                    message=line,
                    tool_source=f"{self.executable} -m py_compile"
                ))
        return errors

class BashSyntaxValidator(SyntaxValidator):
    language_aliases = ["bash", "sh", "shell"]
    default_executable = "bash"

    def validate(self, snippet: CodeSnippet) -> List[SyntaxErrorDetail]:
        errors = []
        if not self.executable: return errors

        command_args = [self.executable, "-n", "{tmp_file}"]
        returncode, stdout, stderr = self._run_external_tool(command_args, snippet.content)

        if returncode != 0:
            # stderr often contains: {tmp_file}: line X: syntax error: ...
            # Parse stderr for line number and message.
            for line in stderr.splitlines():
                 errors.append(SyntaxErrorDetail(
                    doc_path=snippet.doc_path,
                    snippet_start_line=snippet.line_number_start or 0,
                    error_line_in_snippet=1, # Placeholder - needs parsing
                    language=snippet.language or "bash",
                    message=line, # Raw error line
                    tool_source=f"{self.executable} -n"
                ))
        return errors

# Internal validators (not using _run_external_tool directly in the same way)
class YamlSyntaxValidator(SyntaxValidator):
    language_aliases = ["yaml", "yml"]
    # No default_executable as it's internal

    def validate(self, snippet: CodeSnippet) -> List[SyntaxErrorDetail]:
        errors = []
        try:
            import yaml # Ensure PyYAML is available
            yaml.safe_load(snippet.content)
        except yaml.YAMLError as e:
            # Try to extract line/column if available from PyYAML error
            error_line = getattr(e, 'problem_mark', None)
            line_in_snippet = error_line.line + 1 if error_line else 1 # 0-indexed to 1-indexed
            # col_in_snippet = error_line.column + 1 if error_line else 1
            errors.append(SyntaxErrorDetail(
                doc_path=snippet.doc_path,
                snippet_start_line=snippet.line_number_start or 0,
                error_line_in_snippet=line_in_snippet,
                language=snippet.language or "yaml",
                message=str(e),
                tool_source="PyYAML"
            ))
        return errors

class JsonSyntaxValidator(SyntaxValidator):
    language_aliases = ["json"]

    def validate(self, snippet: CodeSnippet) -> List[SyntaxErrorDetail]:
        errors = []
        try:
            import json
            json.loads(snippet.content)
        except json.JSONDecodeError as e:
            errors.append(SyntaxErrorDetail(
                doc_path=snippet.doc_path,
                snippet_start_line=snippet.line_number_start or 0,
                error_line_in_snippet=e.lineno,
                # error_column_in_snippet=e.colno,
                language=snippet.language or "json",
                message=e.msg,
                tool_source="json.loads"
            ))
        return errors

class CodeValidationService:
    def __init__(self, config: Dict[str, Any]): # Parsed code_syntax_validation config
        self.config = config
        self.validators: Dict[str, SyntaxValidator] = {} # lang_canonical_name -> validator_instance
        self._init_validators()

    def _init_validators(self):
        lang_configs = self.config.get("languages", {})

        # Python
        if lang_configs.get("python", {}).get("enabled", False):
            py_conf = lang_configs.get("python", {})
            self.validators["python"] = PythonSyntaxValidator(executable_path=py_conf.get("executable_path"), config=py_conf)
        # Bash
        if lang_configs.get("bash", {}).get("enabled", False):
            bash_conf = lang_configs.get("bash", {})
            self.validators["bash"] = BashSyntaxValidator(executable_path=bash_conf.get("executable_path"), config=bash_conf)
        # YAML
        if lang_configs.get("yaml", {}).get("enabled", False):
            self.validators["yaml"] = YamlSyntaxValidator(config=lang_configs.get("yaml", {}))
        # JSON
        if lang_configs.get("json", {}).get("enabled", False):
            self.validators["json"] = JsonSyntaxValidator(config=lang_configs.get("json", {}))
        # ... Initialize other validators based on config ...

    def _normalize_language_name(self, lang_info_str: str) -> Optional[str]:
        # Simple normalization, can be expanded
        lang_lower = lang_info_str.lower().strip()
        if lang_lower in ["python", "py", "python3"]: return "python"
        if lang_lower in ["javascript", "js"]: return "javascript" # Not implemented yet
        if lang_lower in ["bash", "sh", "shell"]: return "bash"
        if lang_lower in ["yaml", "yml"]: return "yaml"
        if lang_lower == "json": return "json"
        return None # Unrecognized or unsupported

    def validate_snippet(self, snippet: CodeSnippet) -> List[SyntaxErrorDetail]:
        if not snippet.language:
            # Log or handle unspecified language if needed
            return []

        normalized_lang = self._normalize_language_name(snippet.language)
        if not normalized_lang:
            # Log or handle unsupported language
            return []

        validator = self.validators.get(normalized_lang)
        if validator:
            # Check for executable existence for external tools (could be done at init or here)
            # This is a simplified check; actual check might involve `shutil.which`
            if isinstance(validator, (PythonSyntaxValidator, BashSyntaxValidator)) and not validator.executable:
                 # Handle on_missing_tool config: error, warn, or ignore
                if self.config.get("on_missing_tool", "warn") == "warn":
                    print(f"Warning: Executable for {normalized_lang} not found or configured. Skipping validation.")
                # elif self.config.get("on_missing_tool") == "error":
                #    return [SyntaxErrorDetail(..., message=f"Executable for {normalized_lang} not found.")]
                return []
            return validator.validate(snippet)
        return [] # No validator for this language

# Orchestration (within a broader ConsistencyChecker or similar)
# 1. Parse Markdown to get AST.
# 2. Traverse AST to find code blocks (e.g., type 'fence' or 'code_block').
#    For each code block:
#      lang_info = node.info_string (e.g., "python")
#      content = node.content
#      line_start = node.line_number_start
#      snippet = CodeSnippet(content=content, language=lang_info, doc_path=doc_filepath, line_number_start=line_start)
#      errors.extend(code_validation_service.validate_snippet(snippet))
```

### 8. Considerations for External Tools

*   **PATH Dependency:** The default approach assumes standard tools (like `python`, `bash`, `node`) are on the system's PATH.
*   **User-Provided Paths:** The `executable_path` (for the language runtime, e.g., a specific Python version) and `linter_path` (for a specific linter tool if not the default method) in `markitect.yaml` allow users to override this. Markitect must prioritize these paths.
*   **Tool Installation:** Markitect will *not* install these tools. It will be the user's responsibility to ensure they are available if specific methods or paths are configured. The `on_missing_tool` configuration option determines behavior if a tool is not found.
*   **Versioning:** Validating against the *exact* version of a language or tool a project uses can be complex. Using standard system tools provides a good baseline. If very specific versions are needed, users should configure `executable_path` accordingly (e.g., point to a venv's Python).
*   **Security:** Care must be taken when constructing command-line arguments from user inputs (though `executable_path` is from a trusted config file). Using `subprocess.run` with a list of arguments (not `shell=True`) is crucial. Temporary file paths should be handled securely.

This approach provides a solid foundation for basic code syntax validation in Phase 0 by leveraging existing tools, offering configuration flexibility, and clearly defining the scope and error reporting mechanisms.The technical implementation approach document for Phase 0, Deliverable 3.2: Basic Context-Awareness (FR2.2 Code-Awareness: Accuracy - Syntax) has been created.

It is saved as `docs/docmodel_engine/context_awareness_syntax.md`.

The document covers:
1.  **Reiterated Theme/Goal:** Purpose of syntax validation for embedded code snippets.
2.  **Technical Implementation Approach:**
    *   **Code Snippet Extraction:** How snippets are identified from Markdown ASTs, and the `CodeSnippet` data model.
    *   **Language Identification:** Using the info string, normalization of language names, and handling of unspecified/unsupported languages.
    *   **Syntax Validation Strategy:** Chosen approach is wrapping external tools (linters/compilers). Details on how temporary files are used, subprocess execution, and error capturing.
    *   **Supported Languages & Tools (Initial Set):** Python (`python -m py_compile`), JavaScript (`node -c`), Bash (`bash -n`), YAML (`PyYAML`), JSON (`json.loads`).
3.  **Configuration (`markitect.yaml`):** Detailed examples for enabling/disabling the feature, setting paths for executables/linters, language-specific toggles, and the `on_missing_tool` behavior.
4.  **Error Reporting:** How errors are presented, including the `SyntaxErrorDetail` Pydantic model for structured error information.
5.  **Application to Dynamic README Scenario:** Examples of how Python, Bash, and YAML snippets in `README.stub` or `readme_maturity_levels.md` would be validated.
6.  **Core Function Signatures / Class Definitions (Conceptual):**
    *   `CodeSnippet` and `SyntaxErrorDetail` Pydantic models.
    *   `SyntaxValidator` abstract base class.
    *   Concrete validator classes: `PythonSyntaxValidator`, `BashSyntaxValidator`, `YamlSyntaxValidator`, `JsonSyntaxValidator`.
    *   `CodeValidationService` to manage and dispatch to validators.
7.  **Considerations for External Tools:** Discussion on PATH dependencies, user-provided paths, tool installation responsibilities, versioning, and security.

The approach focuses on a practical Phase 0 implementation by leveraging existing external tools, which is generally robust and efficient for common languages.
