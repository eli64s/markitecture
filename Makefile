SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

DOCS_DIR := docs
PYPROJECT_TOML := pyproject.toml
PYPI_VERSION := 0.2.31
PYTHON_VERSION := 3.11
TARGET := src/markitecture
TARGET_TEST := tests

# -------------------------
# Repository Cleanup
# -------------------------

clean: clean-build clean-pyc clean-test ## Remove all build, test, coverage, and Python artifacts

clean-build: ## Remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## Remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## Remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache


# -------------------------
# Development Environment
# -------------------------

.PHONY: build
build: ## Build the distribution package using uv
	uv build
	uv pip install dist/markitecture-$(PYPI_VERSION)-py3-none-any.whl

.PHONY: install
install: ## Install all dependencies from pyproject.toml
	uv sync --dev --group lint --group test --all-extras

.PHONY: lock
lock: ## Lock dependencies declared in pyproject.toml
	uv pip compile $(PYPROJECT_TOML) --all-extras

.PHONY: requirements
requirements: ## Generate requirements files from pyproject.toml
	uv pip compile $(PYPROJECT_TOML) -o requirements.txtiu
	uv pip compile $(PYPROJECT_TOML) --all-extras -o requirements-dev.txt

.PHONY: sync
sync: ## Sync environment with pyproject.toml
	uv sync --all-groups --dev

.PHONY: update
update: ## Update all dependencies from pyproject.toml
	uv lock --upgrade

.PHONY: venv
venv: ## Create a virtual environment
	uv venv --python $(PYTHON_VERSION)


# -------------------------
# Documentation
# -------------------------

.PHONY: docs
docs: ## Serve mintlify documentation locally
	cd $(DOCS_DIR) && npx mintlify dev --verbose


# -------------------------
# Format & Lint
# -------------------------


.PHONY: format-toml
format-toml: ## Format TOML files using pyproject-fmt
	uvx --isolated pyproject-fmt $(TOML_FILE) --indent 4

.PHONY: format
format: ## Format Python files using Ruff
	@echo -e "\n► Running the Ruff formatter..."
	uvx --isolated ruff format $(TARGET)

.PHONY: lint
lint: ## Lint Python files using Ruff
	@echo -e "\n ►Running the Ruff linter..."
	uvx --isolated ruff check $(TARGET) --fix

.PHONY: format-and-lint
format-and-lint: format lint ## Format and lint Python files

.PHONY: typecheck-mypy
typecheck-mypy: ## Type-check Python files using MyPy
	uv run mypy $(TARGET)

.PHONY: typecheck-pyright
typecheck-pyright: ## Type-check Python files using Pyright
	uv run pyright $(TARGET)


# -------------------------
# Tests
# -------------------------

.PHONY: test
test: ## Run test suite using Pytest
	uv run pytest $(TARGET_TEST) --config-file $(PYPROJECT_TOML)


# -------------------------
# CLI Batch Testing
# -------------------------

TEST_DATA := tests/data/readme-ai.md

.PHONY: run-examples
run-examples: ## Run examples for documentation and testing
	@echo -e "\n► Running split commands..."
	uv run markitect --split.i $(TEST_DATA) --split.o examples/text-splitter/header-2 --split.level "##"
	@echo -e "\n--------------------------------------------------------------------------------\n"
	uv run markitect --split.i $(TEST_DATA) --split.o examples/text-splitter/header-3/ --split.level "###"
	@echo -e "\n--------------------------------------------------------------------------------\n"
	uv run markitect --split.i $(TEST_DATA) --split.o examples/text-splitter/header-4/ --split.level "####"
	@echo -e "\n--------------------------------------------------------------------------------\n"
	uv run markitect --reflinks.i tests/data/pydantic.md --reflinks.o examples/reference-links/reflinks_conversion.md
	@echo -e "\n--------------------------------------------------------------------------------\n"
	@echo -e "\n► Checking for markdown files in examples/text-splitter/header-2..."
	@if [ -z "$$(find examples/text-splitter/header-2 -maxdepth 1 -type f -name '*.md')" ]; then \
	  echo "Warning: No markdown files found in examples/text-splitter/header-2. Skipping MkDocs config generation."; \
	else \
	  echo "Generating MkDocs static site config for: examples/text-splitter/header-2"; \
	  uv run markitect --metrics.input $(TEST_DATA) --metrics.style all --metrics.output-dir examples/metrics; \
	fi
	@echo -e "\n--------------------------------------------------------------------------------\n"

.PHONY: run-pypi
run-pypi: ## Run examples for documentation
	uvx --from markitecture markitect --split.i $(TEST_DATA) --split.o examples/text-splitter/pypi/header-2/ --split.level "##"
	uvx --from markitecture markitect --split.i $(TEST_DATA) --split.o examples/text-splitter/pypi/header-3/ --split.level "###"
	uvx --from markitecture markitect --split.i $(TEST_DATA) --split.o examples/text-splitter/pypi/header-4/ --split.level "####"
	uvx --from markitecture markitect --reflinks.i tests/data/pydantic.md --reflinks.o examples/reference-links/reflinks_conversion.md
	uvx --from markitecture --isolated markitect --metrics.input $HOME/Projects/GitHub/readme-ai/README.md --metrics.style all --metrics.output-dir markitet_badges


# -------------------------
# Utils
# -------------------------

bump-version:
	python scripts/bump_version.py src/markitecture/version.py patch


.PHONY: help
help: ## Display this help
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "; printf "\033[1m%-20s %-50s\033[0m\n", "Target", "Description"; \
	              printf "%-20s %-50s\n", "------", "-----------";} \
	      /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %-50s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
