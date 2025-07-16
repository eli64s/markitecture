# Essential Integrations: CI/CD Integration - Basic CLI (Phase 0, Deliverable 4.2)

## Reiterated Theme/Goal

The goal of this deliverable (FR4.2) is to provide a basic Command-Line Interface (CLI) for Markitect. This CLI will enable users to run Markitect's validation capabilities (schema adherence, code syntax, term consistency, link checking) from the command line, making it suitable for integration into CI/CD pipelines. This ensures that documentation quality and consistency are automatically checked as part of the development lifecycle.

## Technical Implementation Approach

### CLI Design

**1. Chosen CLI Framework:**

*   **`Typer`:** This framework will be used for building the Markitect CLI. Typer is built on top of Click and provides modern Python type hints for defining commands and parameters, leading to cleaner and more maintainable code. It offers good autocompletion support and automatic help generation.

**2. Main Command(s) and Subcommands (Phase 0):**

*   **Main Entry Point:** `markitect`
*   **Primary Command (Phase 0):** `markitect validate`
    *   This single command will be the workhorse for Phase 0, performing all configured validation tasks.
    *   Future phases might introduce other commands like `markitect generate` (for FR2.2), `markitect init` (to create a `markitect.yaml`), or `markitect archetype list`.

**3. Key Arguments and Options for `markitect validate`:**

*   **`paths` (Argument):**
    *   `List[Path]`: Optional list of file paths or directory paths to validate.
    *   If provided, these paths will override the `scope.include` and `scope.exclude` settings in `markitect.yaml` for this run.
    *   If not provided, Markitect will use the scope defined in `markitect.yaml`, or default to validating all `.md` files in the project root and its subdirectories if no scope is defined.
*   **`--config` (Option):**
    *   `Optional[Path]`: Path to a specific `markitect.yaml` configuration file.
    *   If not provided, Markitect will search for `markitect.yaml` in the current directory, then parent directories up to the project root (or a sensible limit).
*   **`--project-root` (Option):**
    *   `Optional[Path]`: Specifies the project root directory. This affects where `markitect.yaml` is searched for (if `--config` is not used) and how root-relative paths (e.g., `/docs/file.md` in links or glossaries) are resolved. Defaults to the current working directory.
*   **`--format` (Option):**
    *   `str`: Output format for validation results.
    *   Default: `"human"` (human-readable text).
    *   Phase 0 will implement `"human"`.
    *   Future options: `"json"`, `"checkstyle"` (XML). The design should allow easy addition of new formatters.
*   **`--fix` (Option - Conceptual for Phase 0):**
    *   `bool`: Flag to attempt auto-fixing of certain issues (e.g., formatting, simple term canonicalization).
    *   **For Phase 0, this flag will be recognized but auto-fixing functionality will NOT be implemented.** It's included in the design to reserve the option. The CLI would simply state "Auto-fixing not yet implemented" if used.
*   **`--verbose` / `-v` (Option):**
    *   `bool`: Increase output verbosity (e.g., print files being processed, loaded configurations).
*   **`--quiet` / `-q` (Option):**
    *   `bool`: Suppress all output except for final error summary and exit code. Useful for CI.

### Integration with Markitect Core

1.  **Initialization:**
    *   The CLI command handler will first determine the `project_root` (from option or CWD).
    *   It will then locate and load the `markitect.yaml` configuration file (using the `--config` option or discovery strategy). Markitect's configuration loading module (e.g., using Pydantic models like `MarkitectProjectConfig`) will be used.
    *   If `markitect.yaml` is not found, sensible defaults will be applied, and the user will be informed.

2.  **Service Instantiation:**
    *   Based on the loaded (or default) configuration, the CLI will instantiate the necessary Markitect services:
        *   `MarkdownParserAdapter`
        *   `SchemaLoader`
        *   `ValidatorEngine` (or a facade that uses it)
        *   `ConsistencyChecker` (for terms and links)
        *   `CodeValidationService` (for code syntax)
    *   These services will be configured according to `markitect.yaml`.

3.  **File Discovery and Validation Loop:**
    *   If `paths` argument is provided, those specific files/directories are targeted.
    *   Otherwise, the CLI uses the `scope` from `markitect.yaml` (or defaults) to discover Markdown files to validate, relative to `project_root`.
    *   For each discovered document:
        1.  Read content.
        2.  Parse into AST using `MarkdownParserAdapter`.
        3.  Create a `ParsedDoc` object.
        4.  Perform schema validation using `ValidatorEngine` (loading the appropriate schema for the document based on config or document directives).
        5.  Perform code snippet syntax validation using `CodeValidationService`.
        6.  Perform term consistency and link checking using `ConsistencyChecker`.
    *   All validation results (errors, warnings) are collected.

4.  **Result Aggregation and Output:**
    *   The collected results are passed to an output formatter based on the `--format` option.
    *   The formatter generates the output string (human-readable, JSON, etc.).
    *   The output is printed to `stdout` (for results) and `stderr` (for operational errors/logs).

### Output and Exit Codes

**1. Output Structure:**

*   **Human-Readable (`--format human`, default):**
    *   Summary of files processed.
    *   For each file with errors/warnings:
        *   `FILE: path/to/document.md`
        *   `  L<line> C<col> [<severity>] [<rule_id/source>] <message>`
        *   Example: `  L25 C5 [ERROR] [Markitect:Schema] Missing required element 'Introduction'.`
        *   Example: `  L42 C1 [ERROR] [Markitect:PythonSyntax] SyntaxError: invalid syntax (in snippet starting L38).`
    *   Overall summary: `X files scanned, Y errors, Z warnings found.`
*   **Machine-Readable (Future - e.g., `--format json`):**
    ```json
    {
      "summary": {
        "files_scanned": 10,
        "errors_found": 2,
        "warnings_found": 1
      },
      "results": [
        {
          "filepath": "docs/README.md",
          "errors": [
            {
              "line": 25,
              "column": 5,
              "severity": "ERROR",
              "source": "Markitect:Schema",
              "rule_id": "MissingElement.Introduction",
              "message": "Missing required element 'Introduction'."
            }
          ],
          "warnings": []
        },
        {
          "filepath": "src/example.md",
          "errors": [
            {
              "line": 42, // Absolute line in Markdown
              "column": 1, // Column in Markdown where error occurs
              "severity": "ERROR",
              "source": "Markitect:PythonSyntax",
              "message": "SyntaxError: invalid syntax (in snippet starting L38)."
            }
          ],
          "warnings": [ /* ... */ ]
        }
      ]
    }
    ```

**2. Exit Code Strategy:**

*   **`0`:** Validation successful, no errors found (warnings may be present but don't cause a non-zero exit code by default, unless a `--strict` or `--fail-on-warning` flag is introduced later).
*   **`1` (or other non-zero):** Validation errors found.
*   **`2` (or other distinct non-zero):** Operational error (e.g., invalid configuration, file not found specified in CLI args, tool crash). This helps CI distinguish between linting/validation failures and tool execution failures.

### Configuration Handling

*   **Locating `markitect.yaml`:**
    1.  If `--config <path>` is provided, use that path.
    2.  Else, if `--project-root <dir>` is provided, search for `markitect.yaml` in `<dir>`.
    3.  Else, search in the current working directory, then recursively search parent directories up to a sensible limit (e.g., repository root identified by `.git` or filesystem root).
*   **`project_root` Determination:**
    1.  If `--project-root <dir>` is provided, use that.
    2.  Else, if `--config <path>` is used, `project_root` is the directory containing the specified config file.
    3.  Else (config file discovered via search), `project_root` is the directory where `markitect.yaml` was found.
    4.  If no config file is found, `project_root` defaults to the current working directory.
*   **Overrides:**
    *   CLI `paths` argument for files/directories to validate overrides `consistency_checks.scope` from `markitect.yaml`.
    *   Future: Options like `--enable-check <check_name>` or `--schema <path>` could override specific config settings. For Phase 0, path override is primary.

### Application to Dynamic README Scenario

Consider a project with `readme_maturity_levels.md` (RML) and `README.stub`.
`markitect.yaml` might be configured like this (conceptual):

```yaml
# markitect.yaml
project_root: "."
# Schemas defined or referenced
schemas:
  ReadmeMaturityFramework: "path/to/ReadmeMaturityFrameworkSchema.yaml"
  MyProjectReadmeStub: "path/to/MyProjectReadmeStubSchema.yaml"

# Document to schema mapping
document_schema_map:
  "readme_maturity_levels.md": "ReadmeMaturityFramework"
  "README.stub": "MyProjectReadmeStub"

consistency_checks:
  scope:
    include:
      - "readme_maturity_levels.md"
      - "README.stub"
  # ... term_consistency, link_checking, code_syntax_validation configs ...
```

**CLI Usage:**

1.  **Default run (uses config):**
    ```bash
    markitect validate
    ```
    *   Markitect finds `markitect.yaml`.
    *   It identifies `readme_maturity_levels.md` and `README.stub` from the `scope` (or `document_schema_map` implies scope).
    *   Validates `readme_maturity_levels.md` against the "ReadmeMaturityFramework" schema.
    *   Validates `README.stub` against the "MyProjectReadmeStub" schema.
    *   Performs configured link, term, and code syntax checks on both files.
    *   Outputs results. If errors, exits with non-zero code.

2.  **Validate specific file (overrides scope):**
    ```bash
    markitect validate README.stub
    ```
    *   Markitect validates *only* `README.stub`.
    *   It still loads `markitect.yaml` to find the schema for `README.stub` (from `document_schema_map`) and other validation settings.
    *   Performs all checks on `README.stub`.

**Output Example (Human-readable, if `README.stub` has an error):**

```
Markitect Validator v0.1.0
Project Root: /path/to/project
Configuration: /path/to/project/markitect.yaml

Processing: README.stub
FILE: README.stub
  L15 C4 [ERROR] [Markitect:Schema] Element 'ProjectOverview': Missing required child 'ShortDescription'.
  L22 C1 [ERROR] [Markitect:PythonSyntax] SyntaxError: invalid syntax (in snippet starting L20).

Processing: readme_maturity_levels.md
(No errors reported for this file)

Summary:
2 files scanned.
2 errors found.
0 warnings found.

Validation FAILED.
```
(CLI exits with code 1)

### Core Function Signatures / Class Definitions (Conceptual - CLI specific)

```python
import typer
from typing import List, Optional
from pathlib import Path

app = typer.Typer(help="Markitect: Intelligent Markdown Documentation Toolkit.")

# Global state or context object (optional, can be passed around)
# class CliContext:
#    project_root: Path
#    config: MarkitectProjectConfig
#    # ... services ...

def _setup_services(project_root: Path, config_path: Optional[Path]):
    """Loads config and initializes Markitect core services."""
    # Locate and load markitect.yaml
    # effective_project_root, effective_config_path = resolve_config_paths(...)
    # project_config = load_project_config(effective_config_path)
    # Instantiate MarkdownParserAdapter, SchemaLoader, ValidatorEngine, CodeValidationService, ConsistencyChecker
    # Return a context object or a tuple of services
    # For Phase 0, this logic might be directly in the validate_command.
    pass


@app.command(name="validate", help="Validate Markdown documents against Markitect rules.")
def validate_command(
    paths: Optional[List[Path]] = typer.Argument(
        None,
        help="Paths to specific Markdown files or directories to validate. Overrides 'scope' in config.",
        exists=True, # Typer will check if paths exist
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to markitect.yaml configuration file.",
        exists=True,
        dir_okay=False,
    ),
    project_root: Optional[Path] = typer.Option(
        None,
        "--project-root",
        "-p",
        help="Project root directory. Defaults to where markitect.yaml is found or CWD.",
        exists=True,
        file_okay=False,
        resolve_path=True, # Typer resolves to absolute path
    ),
    output_format: str = typer.Option(
        "human",
        "--format",
        "-f",
        help="Output format ('human', 'json', 'checkstyle' - future).",
    ),
    fix: bool = typer.Option(
        False,
        "--fix",
        help="Attempt to auto-fix issues (Not implemented in Phase 0).",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress all output except summary."),
):
    """
    Main validation logic.
    1. Determine project_root and config_file_path.
    2. Load MarkitectProjectConfig.
    3. Initialize Markitect services (parser, validators).
    4. Determine target files (from 'paths' arg or config scope).
    5. For each target file:
       - Read content.
       - Parse.
       - Run all configured validations (schema, code, consistency).
       - Collect errors/warnings.
    6. Format and print results using selected 'output_format'.
    7. Set exit code.
    """
    if fix:
        typer.echo("Warning: --fix option is not yet implemented.", err=True)

    # ... (Actual implementation using Markitect core services) ...

    # Example of how processing might look:
    # resolved_project_root, config_model = load_configuration(project_root_opt, config_opt)
    # validation_runner = ValidationRunner(config_model, resolved_project_root) # Conceptual class

    # if paths_arg:
    #    target_files_to_scan = resolve_cli_paths_to_files(paths_arg, resolved_project_root)
    # else:
    #    target_files_to_scan = discover_files_from_scope(config_model.consistency_checks.scope, resolved_project_root)

    # all_diagnostics = []
    # for file_path in target_files_to_scan:
    #    diagnostics_for_file = validation_runner.validate_file(file_path)
    #    all_diagnostics.extend(diagnostics_for_file)

    # output_str = format_diagnostics(all_diagnostics, output_format)
    # if not quiet:
    #    typer.echo(output_str)

    # num_errors = count_errors(all_diagnostics)
    # if num_errors > 0:
    #    if not quiet:
    #        typer.secho(f"\nValidation FAILED: {num_errors} error(s) found.", fg=typer.colors.RED, bold=True)
    #    raise typer.Exit(code=1)
    # else:
    #    if not quiet:
    #        typer.secho("\nValidation PASSED.", fg=typer.colors.GREEN)

    # Placeholder logic:
    typer.echo(f"Simulating validation for paths: {paths}")
    typer.echo(f"Config path: {config}, Project root: {project_root}")
    typer.echo(f"Format: {output_format}, Verbose: {verbose}, Quiet: {quiet}")

    # Simulate finding an error for exit code testing
    found_errors = True # Simulate some errors for now
    if found_errors:
        if not quiet:
            typer.secho("Validation FAILED (simulated).", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    else:
        if not quiet:
            typer.secho("Validation PASSED (simulated).", fg=typer.colors.GREEN)


# Main entry point for the CLI application
# if __name__ == "__main__":
#    app() # Typer creates the CLI app from this
```

### Example CI/CD Usage (Conceptual)

**GitHub Actions Workflow (`.github/workflows/docs-lint.yml`):**

```yaml
name: Documentation Linting

on: [pull_request]

jobs:
  markitect-validate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.9' # Specify your project's Python version

      - name: Install Markitect
        run: |
          python -m pip install --upgrade pip
          pip install . # Assuming Markitect is installable from pyproject.toml
          # Or: pip install markitect (if published to PyPI)

      - name: Run Markitect validation
        run: |
          markitect validate --project-root ./ # Explicitly set project root
          # Or if specific files/dirs for CI:
          # markitect validate docs/guide/ src/tutorials/
          # For machine-readable output in CI (future):
          # markitect validate --format json --output-file markitect-results.json

      # Future: Upload artifacts (e.g., markitect-results.json)
      # - name: Upload Markitect results
      #   if: always() # Run even if previous step failed
      #   uses: actions/upload-artifact@v3
      #   with:
      #     name: markitect-validation-results
      #     path: markitect-results.json
```

This structure provides a robust CLI for Phase 0, focusing on core validation tasks and clear integration points for CI/CD systems. The use of Typer simplifies development and provides a good user experience.Okay, I have created the new Markdown document for Phase 0, Deliverable 4.2.

It is saved as: `docs/docmodel_engine/ci_cd_integration_cli.md`

The document covers:
1.  **Reiterated Theme/Goal:** The purpose of CI/CD integration via a CLI.
2.  **Technical Implementation Approach:**
    *   **CLI Design:**
        *   Chosen CLI framework: `Typer`.
        *   Main command: `markitect validate`.
        *   Key arguments and options: `paths`, `--config`, `--project-root`, `--format`, `--fix` (conceptual), `--verbose`, `--quiet`.
    *   **Integration with Markitect Core:** How the CLI initializes and uses Markitect's services (config loader, parser, validators).
    *   **Output and Exit Codes:** Structure for human-readable output (and future JSON), and a clear exit code strategy (0 for success, non-zero for validation or operational errors).
3.  **Configuration Handling:** Strategy for locating `markitect.yaml`, determining `project_root`, and handling CLI overrides.
4.  **Application to Dynamic README Scenario:** Detailed example of using `markitect validate` with `readme_maturity_levels.md` and `README.stub`, including how schemas and checks would apply, and example human-readable output for errors.
5.  **Core Function Signatures / Class Definitions (Conceptual - CLI specific):** A conceptual Typer application structure with the `validate_command` function.
6.  **Example CI/CD Usage (Conceptual):** A snippet for a GitHub Actions workflow demonstrating how `markitect validate` could be integrated.

The plan focuses on a simple yet effective CLI for Phase 0, leveraging `Typer` for a modern CLI experience and ensuring clear CI/CD integration via exit codes and configurable behavior.Okay, I have created the new Markdown document for Phase 0, Deliverable 4.2.

It is saved as: `docs/docmodel_engine/ci_cd_integration_cli.md`

The document covers:
1.  **Reiterated Theme/Goal:** The purpose of CI/CD integration via a CLI.
2.  **Technical Implementation Approach:**
    *   **CLI Design:**
        *   Chosen CLI framework: `Typer`.
        *   Main command: `markitect validate`.
        *   Key arguments and options: `paths`, `--config`, `--project-root`, `--format`, `--fix` (conceptual), `--verbose`, `--quiet`.
    *   **Integration with Markitect Core:** How the CLI initializes and uses Markitect's services (config loader, parser, validators).
    *   **Output and Exit Codes:** Structure for human-readable output (and future JSON), and a clear exit code strategy (0 for success, non-zero for validation or operational errors).
3.  **Configuration Handling:** Strategy for locating `markitect.yaml`, determining `project_root`, and handling CLI overrides.
4.  **Application to Dynamic README Scenario:** Detailed example of using `markitect validate` with `readme_maturity_levels.md` and `README.stub`, including how schemas and checks would apply, and example human-readable output for errors.
5.  **Core Function Signatures / Class Definitions (Conceptual - CLI specific):** A conceptual Typer application structure with the `validate_command` function.
6.  **Example CI/CD Usage (Conceptual):** A snippet for a GitHub Actions workflow demonstrating how `markitect validate` could be integrated.

The plan focuses on a simple yet effective CLI for Phase 0, leveraging `Typer` for a modern CLI experience and ensuring clear CI/CD integration via exit codes and configurable behavior.
