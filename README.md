<div id="top" align="center">

<!-- HEADER -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/eli64s/splitme/77bec69129dd3a075d7d0816c7bd826da131ccc7/docs/assets/splitme-circle-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/eli64s/splitme/77bec69129dd3a075d7d0816c7bd826da131ccc7/docs/assets/splitme-circle-light.svg">
  <img alt="splitme Logo" src="https://raw.githubusercontent.com/eli64s/splitme/77bec69129dd3a075d7d0816c7bd826da131ccc7/docs/assets/splitme-circle-light.svg" width="900" style="max-width: 100%;">
</picture>

<h3 align="center">
  Powerful markdown tools for modern documentation
</h3>

<p align="center">
  <em>Build, manage, and scale your documentation workflows.</em>
</p>

<!-- BADGES -->
<div align="center">
  <p align="center" style="margin-bottom: 20px;">
    <a href="https://github.com/eli64s/splitme/actions">
      <img src="https://img.shields.io/github/actions/workflow/status/eli64s/splitme/ci.yml?label=CI&style=flat&logo=githubactions&logoColor=white&labelColor=2A2A2A&color=FFD700" alt="GitHub Actions" />
    </a>
    <a href="https://app.codecov.io/gh/eli64s/splitme">
      <img src="https://img.shields.io/codecov/c/github/eli64s/splitme?label=Coverage&style=flat&logo=codecov&logoColor=white&labelColor=2A2A2A&color=3fe1c0" alt="Coverage" />
    </a>
    <a href="https://pypi.org/project/splitme/">
      <img src="https://img.shields.io/pypi/v/splitme-ai?label=PyPI&style=flat&logo=pypi&logoColor=white&labelColor=2A2A2A&color=00E5FF" alt="PyPI Version" />
    </a>
    <a href="https://github.com/eli64s/splitme">
      <img src="https://img.shields.io/pypi/pyversions/splitme-ai?label=Python&style=flat&logo=python&logoColor=white&labelColor=2A2A2A&color=7934C5" alt="Python Version" />
    </a>
    <a href="https://opensource.org/license/mit/">
      <img src="https://img.shields.io/github/license/eli64s/splitme?label=License&style=flat&logo=opensourceinitiative&logoColor=white&labelColor=2A2A2A&color=FF00FF" alt="MIT License">
    </a>
  </p>
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/eli64s/splitme/216a92894e6f30c707a214fad5a5fba417e3bc39/docs/assets/line.svg" alt="separator" width="100%" height="2px" style="margin: 20px 0;">
</div>

</div>
<!-- HEADER END -->

## What is Splitme?

Splitme is a comprehensive Python toolkit designed to streamline your Markdown workflow. Whether you're managing documentation, writing technical content, or maintaining a knowledge base, Splitme provides essential utilities to make working with Markdown files easier and more efficient.

__Core Features:__

- **Text Splitting:** Break down large Markdown files into manageable sections based on headings or custom rules.
- **Link Management:** Convert between inline and reference-style links, validate URLs, and identify broken links.
- **Content Analysis:** Analyze document structure, extract metadata, and ensure consistent formatting.
- **Documentation Tools:** Generate configurations for static site generators like [MkDocs][mkdocs] and maintain organized documentation.

---

## Quick Start

### Installation

Install from [PyPI][pypi] using your preferred package manager.

#### <img width="2%" src="https://simpleicons.org/icons/python.svg">&emsp13;pip

Use [pip][pip] (recommended for most users):

```sh
pip install -U splitme
```

#### <img width="2%" src="https://simpleicons.org/icons/pipx.svg">&emsp13;pipx

Install in an isolated environment with [pipx][pipx]:

```sh
❯ pipx install splitme
```

#### <img width="2%" src="https://simpleicons.org/icons/uv.svg">&emsp13;uv

For the fastest installation use [uv][uv]:

```sh
❯ uv tool install splitme
```

### Using the CLI

#### Text Splitting

Split large Markdown files into smaller, organized sections:

```sh
splitme \
    --split.i tests/data/markdown/readme-ai.md \
    --split.o docs/examples/split-sections-h2
```

#### Link Validation

Check for broken links in your documentation:

```sh
splitme --check-links.input tests/data/markdown/pydantic.md
```

You will see a summary of the broken links in your terminal:

```console

Markdown Link Check Results

┏━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Status ┃ Line ┃ Link                                                                              ┃ Error    ┃
┡━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ ✓      │ 2    │ https://img.shields.io/github/actions/workflow/status/pydantic/pydantic/ci.yml?b… │          │
│ ✓      │ 3    │ https://coverage-badge.samuelcolvin.workers.dev/pydantic/pydantic.svg             │          │
│ ✓      │ 4    │ https://img.shields.io/pypi/v/pydantic.svg                                        │          │
│ ✓      │ 5    │ https://img.shields.io/conda/v/conda-forge/pydantic.svg                           │          │
│ ✓      │ 6    │ https://static.pepy.tech/badge/pydantic/month                                     │          │
│ ✓      │ 7    │ https://img.shields.io/pypi/pyversions/pydantic.svg                               │          │
│ ✓      │ 8    │ https://img.shields.io/github/license/pydantic/pydantic.svg                       │          │
│ ✓      │ 9    │ https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/p… │          │
│ ✓      │ 18   │ https://pydantic.dev/articles/logfire-announcement                                │          │
│ ✓      │ 24   │ https://docs.pydantic.dev/                                                        │          │
│ ✓      │ 24   │ https://github.com/pydantic/pydantic/tree/1.10.X-fixes                            │          │
│ ✓      │ 28   │ https://docs.pydantic.dev/                                                        │          │
│ 𝗫      │ 34   │ https://docs.pydantic.dev/install/invalid-link                                    │ HTTP 404 │
└────────┴──────┴───────────────────────────────────────────────────────────────────────────────────┴──────────┘

Summary: 1 broken links out of 13 total links.
```

#### Reference Link Conversion

Convert inline links to reference-style for better maintainability:

```sh
splitme --reflinks.input tests/data/markdown/pydantic.md --reflinks.output with_refs.md
```

#### Static Site Documentation Generation

Generate a MkDocs configuration [mkdocs.yml] file from a Markdown document:

```sh
splitme \
    --split.i tests/data/markdown/readme-ai.md \
    --split.o docs/examples/split-sections-h2 \
    --mkdocs.dir docs/examples/split-sections-h2 \
    --mkdocs.site-name "MyDocs"
```

View the output of all examples above [here][examples].

<!--
>[!NOTE]
> Explore the [Official Documentation][docs] for more detailed guides and examples.
-->

---

<!--
## Advanced Features

### Content Analysis
- **Structure Analysis:** Analyze heading hierarchy and document structure
- **Link Extraction:** Extract and manage all links in your documentation
- **Metadata Management:** Handle front matter and document metadata
- **Format Consistency:** Ensure consistent formatting across documents

### Documentation Tools
- **Static Site Integration:** Generate configurations for popular static site generators
- **Navigation Management:** Create and maintain navigation structures
- **Asset Management:** Track and validate document assets and dependencies
- **Custom Templates:** Support for custom templates and layouts

## Configuration

Create a `splitme.yaml` for advanced configuration:

```yaml
# Core utility settings
utilities:
  text_splitting:
    heading_levels: [1, 2, 3]
    preserve_context: true
    min_section_length: 500

  link_management:
    validate_urls: true
    reference_style: true
    broken_link_reporting: true

  content_analysis:
    structure_validation: true
    metadata_extraction: true
    format_checking: true

# Output settings
output:
  format: mkdocs
  theme: material
  syntax_highlight: true
```

## Configuration

Create a `splitme.yaml` for advanced configuration:

```yaml
# Core splitting settings
split:
  min_length: 500
  max_length: 2000
  preserve_context: true
  smart_splitting: true

# Content analysis settings
analysis:
  enable_clustering: true
  min_topic_coherence: 0.7
  language_detection: true

# Output settings
output:
  format: mkdocs
  theme: material
  syntax_highlight: true
  math_support: true

# Integration settings
integrations:
  github:
    enable_pages: true
    branch: gh-pages
  search:
    engine: elasticsearch
    index_name: docs
```

---
-->

## Roadmap

- [ ] Support for additional documentation formats (e.g., reStructuredText, HTML)
- [ ] Add more intuitive CLI commands and options.
- [ ] Integration with more static site generators
- [ ] Plugin system for custom utilities
- [ ] Enhanced content analysis features

---

## Contributing

Contributions are welcome! Whether it's bug reports, feature requests, or code contributions, please feel free to:

1. Open an [issue][github-issues]
2. Submit a [pull request][github-pulls]
3. Improve documentation
4. Share your ideas

---

## License

<!--
Copyright © 2024-2025 [splitme][splitme]. <br />
Released under the [MIT][mit-license] license.
-->

Splitme is released under the [MIT license][mit-license] <br />
Copyright © 2024-2025 [Splitme][splitme]

<div align="left">
  <a href="#top">
    <img src="https://raw.githubusercontent.com/eli64s/splitme/77bec69129dd3a075d7d0816c7bd826da131ccc7/docs/assets/buttons/rectangle.svg" width="100px" height="100px" alt="Return to Top">
  </a>
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/eli64s/splitme/216a92894e6f30c707a214fad5a5fba417e3bc39/docs/assets/line.svg" alt="separator" width="100%" height="2px" style="margin: 20px 0;">
</div>


<!-- REFERENCE LINKS -->

<!-- PROJECT RESOURCES -->
[pypi]: https://pypi.org/project/splitme/
[splitme]: https://github.com/eli64s/splitme
[github-issues]: https://github.com/eli64s/splitme/issues
[github-pulls]: https://github.com/eli64s/splitme/pulls
[mit-license]: https://github.com/eli64s/splitme/blob/main/LICENSE
[examples]: https://github.com/eli64s/splitme/tree/main/docs/examples

<!-- DEV TOOLS -->
[python]: https://www.python.org/
[pip]: https://pip.pypa.io/en/stable/
[pipx]: https://pipx.pypa.io/stable/
[uv]: https://docs.astral.sh/uv/
[mkdocs]: https://www.mkdocs.org/
[mkdocs.yml]: https://www.mkdocs.org/user-guide/configuration/
