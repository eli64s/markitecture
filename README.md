<div id="top" align="center">

<!-- HEADER -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/eli64s/splitme-ai/ed2534164a2f7f2a7b4aafef998127791b205f30/docs/assets/logo-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/eli64s/splitme-ai/ed2534164a2f7f2a7b4aafef998127791b205f30/docs/assets/logo-light.svg">
  <img alt="SplitMe-AI Logo" src="https://raw.githubusercontent.com/eli64s/splitme-ai/ed2534164a2f7f2a7b4aafef998127791b205f30/docs/assets/logo-light.svg" width="900" style="max-width: 100%;">
</picture>

<h3 align="center">
  Break down your docs. Build up your knowledge.
</h3>

<p align="center">
  <em>A Markdown text splitter for modular docs and maximum flexibility.</em>
</p>

<!-- BADGES -->
<div align="center">
  <p align="center" style="margin-bottom: 20px;">
    <a href="https://github.com/eli64s/splitme-ai/actions">
      <img src="https://img.shields.io/github/actions/workflow/status/eli64s/splitme-ai/ci.yml?label=CI&style=flat&logo=githubactions&logoColor=white&labelColor=2A2A2A&color=ffd700" alt="GitHub Actions" />
    </a>
    <a href="https://app.codecov.io/gh/eli64s/splitme-ai">
      <img src="https://img.shields.io/codecov/c/github/eli64s/splitme-ai?label=Coverage&style=flat&logo=codecov&logoColor=white&labelColor=2A2A2A&color=3fe1c0" alt="Coverage" />
    </a>
    <a href="https://pypi.org/project/splitme-ai/">
      <img src="https://img.shields.io/pypi/v/splitme-ai?label=PyPI&style=flat&logo=pypi&logoColor=white&labelColor=2A2A2A&color=3d8be1" alt="PyPI Version" />
    </a>
    <a href="https://github.com/eli64s/splitme-ai">
      <img src="https://img.shields.io/pypi/pyversions/splitme-ai?label=Python&style=flat&logo=python&logoColor=white&labelColor=2A2A2A&color=9b26d4" alt="Python Version" />
    </a>
    <a href="https://opensource.org/license/mit/">
      <img src="https://img.shields.io/github/license/eli64s/splitme-ai?label=License&style=flat&logo=opensourceinitiative&logoColor=white&labelColor=2A2A2A&color=ff00ff" alt="MIT License">
    </a>
  </p>
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/eli64s/splitme-ai/216a92894e6f30c707a214fad5a5fba417e3bc39/docs/assets/line.svg" alt="separator" width="100%" height="2px" style="margin: 20px 0;">
</div>

</div>

## What is SplitmeAI?

SplitmeAI is a Python module that addresses challenges in managing large Markdown files, particularly when creating and maintaining structured static documentation sites such as [Mkdocs][mkdocs].

__Key Features:__

- **Section Splitting:** Breaks down large Markdown files into smaller, manageable sections based on specified heading levels.
- **Hierarchy Preservation:** Maintains parent heading context within each split file.
- **Filename Sanitization:** Generates clean, unique filenames for each section, ensuring compatibility and readability.
- **Reference Link Management:** Extracts and appends reference-style links used within each section.
- **Reference Link Conversion:** Convert all inline links to reference-style links for improved readability and maintainability.
- **Link Validation:** Checks and validates all links within a Markdown file for accuracy and integrity.
- **Thematic Break Handling:** Recognizes and handles line breaks (`---`, `***`, `___`) for intelligent content segmentation.
- **MkDocs Integration:** Automatically generates an `mkdocs.yml` configuration file based on the split sections.
- **CLI Support:** Provides a user-friendly Command-Line Interface for seamless operation.

---

## Quick Start

### Installation

Install from [PyPI][pypi] using your preferred package manager listed below.

#### <img width="2%" src="https://simpleicons.org/icons/python.svg">&emsp13;pip

Use [pip][pip] (recommended for most users):

```sh
pip install -U splitme-ai
```

#### <img width="2%" src="https://simpleicons.org/icons/pipx.svg">&emsp13;pipx

Install in an isolated environment with [pipx][pipx]:

```sh
❯ pipx install splitme-ai
```

#### <img width="2%" src="https://simpleicons.org/icons/uv.svg">&emsp13;uv

For the fastest installation use [uv][uv]:

```sh
❯ uv tool install splitme-ai
```

### Usage

#### Using the CLI

Let's take a look at some examples of how to use the `splitme-ai` CLI.

##### Splitting a Markdown File

__Example 1:__ Split a Markdown file on heading level 2 (default setting):

```sh
splitme-ai \
    --split.i docs/examples/data/README-AI.md \
    --split.settings.o docs/examples/output-h2
```

__Example 2:__ Split on heading level 2 and generate an [mkdocs.yml] configuration file:

```sh
splitme-ai \
    --split.i docs/examples/data/README-AI.md \
    --split.settings.o docs/examples/output-h2 \
    --split.settings.mkdocs
```

__Example 3:__ Split on heading level 3:

```sh
splitme-ai \
    --split.i docs/examples/data/README-AI.md \
    --split.settings.o docs/examples/output-h3 \
    --split.settings.hl "###"
```

__Example 4:__ Split on heading level 4:

```sh
splitme-ai \
    --split.i docs/examples/data/README-AI.md \
    --split.settings.o docs/examples/output-h4 \
    --split.settings.hl "####"
```

##### Converting Reference Links

__Example 5:__ Convert inline links to reference-style links:

```sh
splitme-ai --reflinks.i tests/data/pydantic.md --reflinks.o with_reflinks.md
```

##### Validating Links

__Example 6:__ Validate all links in a Markdown file:

```sh
splitme-ai --validate-links.i tests/data/pydantic.md
```

The output will display the results of whether the links are valid or broken.

```console
Scanning markdown file tests/data/pydantic.md for broken links...

Markdown Link Check Results:
--------------------------------------------------------------------------------
✓ Line 2: [![CI](https://img.shields.io/github/actions/workflow/status/pydantic/pydantic/ci.yml?branch=main&logo=github&label=CI)
✓ Line 3: [![Coverage](https://coverage-badge.samuelcolvin.workers.dev/pydantic/pydantic.svg)
✓ Line 4: [![pypi](https://img.shields.io/pypi/v/pydantic.svg)
✓ Line 5: [![CondaForge](https://img.shields.io/conda/v/conda-forge/pydantic.svg)
✓ Line 6: [![downloads](https://static.pepy.tech/badge/pydantic/month)
✓ Line 7: [![versions](https://img.shields.io/pypi/pyversions/pydantic.svg)
✓ Line 8: [![license](https://img.shields.io/github/license/pydantic/pydantic.svg)
✓ Line 9: [![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)
✓ Line 18: [Learn more](https://pydantic.dev/articles/logfire-announcement)
✓ Line 24: [pydantic V1.10 Documentation](https://docs.pydantic.dev/)
✓ Line 24: [`1.10.X-fixes` git branch](https://github.com/pydantic/pydantic/tree/1.10.X-fixes)
✓ Line 28: [documentation](https://docs.pydantic.dev/)
✓ Line 34: [Install](https://docs.pydantic.dev/install/)

Summary: 0 broken links out of 13 total links.
```

View the output of all examples above [here][examples].

>[!NOTE]
> Explore the [Official Documentation][docs] for more detailed guides and examples.

---

## Roadmap

- [X] Implement reference link conversion and management.
- [ ] Enhance CLI usability and user experience.
- [ ] Integrate AI-powered content analysis and segmentation.
- [ ] Add robust chunking and splitting algorithms for LLM applications.
- [ ] Add support for additional static site generators.
- [ ] Add support for additional input and output formats.

---

## Contributing

Contributions are welcome! For bug reports, feature requests, or questions, please [open an issue][github-issues] or submit a [pull request][github-pulls] on GitHub.

---

## License

Copyright © 2024-2025 [splitme-ai][splitme-ai]. <br />
Released under the [MIT][mit-license] license.

<div align="left">
  <a href="#top">
    <img src="https://raw.githubusercontent.com/eli64s/splitme-ai/216a92894e6f30c707a214fad5a5fba417e3bc39/docs/assets/button.svg" width="100px" height="100px" alt="Return to Top">
  </a>
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/eli64s/splitme-ai/216a92894e6f30c707a214fad5a5fba417e3bc39/docs/assets/line.svg" alt="separator" width="100%" height="2px" style="margin: 20px 0;">
</div>

<!-- REFERENCE LINKS -->

<!-- PROJECT RESOURCES -->
[pypi]: https://pypi.org/project/splitme-ai/
[splitme-ai]: https://github.com/eli64s/splitme-ai
[github-issues]: https://github.com/eli64s/splitme-ai/issues
[github-pulls]: https://github.com/eli64s/splitme-ai/pulls
[mit-license]: https://github.com/eli64s/splitme-ai/blob/main/LICENSE
[examples]: https://github.com/eli64s/splitme-ai/tree/main/docs/examples

<!-- DEV TOOLS -->
[python]: https://www.python.org/
[pip]: https://pip.pypa.io/en/stable/
[pipx]: https://pipx.pypa.io/stable/
[uv]: https://docs.astral.sh/uv/
[mkdocs]: https://www.mkdocs.org/
[mkdocs.yml]: https://www.mkdocs.org/user-guide/configuration/
