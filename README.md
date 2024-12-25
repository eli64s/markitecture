<div id="top" align="center">

<!-- HEADER -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/eli64s/splitme-ai/3ef5d52975c2a237f2b245cd15c9e091631e2d5f/docs/assets/logo-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/eli64s/splitme-ai/3ef5d52975c2a237f2b245cd15c9e091631e2d5f/docs/assets/logo-light.svg">
  <img alt="SplitMe-AI Logo" src="https://raw.githubusercontent.com/eli64s/splitme-ai/3ef5d52975c2a237f2b245cd15c9e091631e2d5f/docs/assets/logo-light.svg" width="800" style="max-width: 100%;">
</picture>

<!--
<img src="https://raw.githubusercontent.com/eli64s/splitme-ai/3ef5d52975c2a237f2b245cd15c9e091631e2d5f/docs/assets/logo-light.svg#gh-light-mode-only" alt="SplitMe-AI Logo Light" width="800" style="max-width: 100%;">
<img src="https://raw.githubusercontent.com/eli64s/splitme-ai/3ef5d52975c2a237f2b245cd15c9e091631e2d5f/docs/assets/logo-dark.svg#gh-dark-mode-only" alt="SplitMe-AI Logo Dark" width="800" style="max-width: 100%;"> 
-->

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
      <img src="https://img.shields.io/github/actions/workflow/status/eli64s/splitme-ai/ci.yml?label=CI&style=flat&logo=githubactions&logoColor=white&color=FFD700&labelColor=2A2A2A" alt="GitHub Actions" />
    </a>
    <a href="https://app.codecov.io/gh/eli64s/splitme-ai">
      <img src="https://img.shields.io/codecov/c/github/eli64s/splitme-ai?label=Coverage&style=flat&labelColor=2A2A2A&logo=codecov&logoColor=white&color=20B2AA" alt="Coverage" />
    </a>
    <a href="https://pypi.org/project/splitme-ai/">
      <img src="https://img.shields.io/pypi/v/splitme-ai?label=PyPI&logo=pypi&labelColor=2A2A2A&style=flat&logoColor=white&color=00E5FF" alt="PyPI Version" />
    </a>
    <a href="https://github.com/eli64s/splitme-ai">
      <img src="https://img.shields.io/pypi/pyversions/splitme-ai?label=Python&labelColor=2A2A2A&style=flat&logo=python&logoColor=white&color=7934C5" alt="Python Version" />
    </a>
    <a href="https://opensource.org/license/mit/">
      <img src="https://img.shields.io/github/license/eli64s/splitme-ai?label=License&style=flat&labelColor=2A2A2A&logo=opensourceinitiative&logoColor=white&color=FF00FF" alt="MIT License">
  </a>
  </p>
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/eli64s/splitme-ai/216a92894e6f30c707a214fad5a5fba417e3bc39/docs/assets/line.svg" alt="separator" width="100%" height="2px" style="margin: 20px 0;">
</div>

</div>

## What is SplitmeAI?

`SplitmeAI` is a Python module that addresses challenges in managing large Markdown files, particularly when creating and maintaining structured static documentation websites such as [Mkdocs][mkdocs].

__Key Features:__

- **Section Splitting:** Breaks down large Markdown files into smaller, manageable sections based on specified heading levels.
- **Filename Sanitization:** Generates clean, unique filenames for each section, ensuring compatibility and readability.
- **Reference Link Management:** Extracts and appends reference-style links used within each section.
- **Hierarchy Preservation:** Maintains parent heading context within each split file.
- **Thematic Break Handling:** Recognizes and handles line breaks (`---`, `***`, `___`) for intelligent content segmentation.
- **MkDocs Integration:** Automatically generates an `mkdocs.yml` configuration file based on the split sections.
- **CLI Support:** Provides a user-friendly Command-Line Interface for seamless operation.

---

## Quick Start

### Installation

Install from [PyPI][pypi] using any of the package managers listed below.

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

__Example 1:__ Split a Markdown file on heading level 2 (default setting):

```sh
splitme-ai \
    --split.i examples/data/README-AI.md \
    --split.settings.o examples/output-h2
```

__Example 2:__ Split on heading level 2 and generate an [mkdocs.yml] configuration file:

```sh
splitme-ai \
    --split.i examples/data/README-AI.md \
    --split.settings.o examples/output-h2 \
    --split.settings.mkdocs
```

View the output generated for [splitting on heading level 2 here](./examples/output-h2).

__Example 3:__ Split on heading level 3:

```sh
splitme-ai \
    --split.i examples/data/README-AI.md \
    --split.settings.o examples/output-h3 \
    --split.settings.hl "###"
```

View the output generated for [splitting on heading level 3 here](./examples/output-h3).

__Example 4:__ Split on heading level 4:

```sh
splitme-ai \
    --split.i examples/data/README-AI.md \
    --split.settings.o examples/output-h4 \
    --split.settings.hl "####"
```

View the output generated for [splitting on heading level 4 here](./examples/output-h4).

>[!NOTE]
> The Official Documentation site with extensive examples and usage instructions is under development Stay tuned for updates!

---

## Roadmap

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

Copyright © 2024 [splitme-ai][splitme-ai]. <br />
Released under the [MIT][mit-license] license.

<div align="left">
  <a href="#top">
    <img src="https://raw.githubusercontent.com/eli64s/splitme-ai/216a92894e6f30c707a214fad5a5fba417e3bc39/docs/assets/button-circles.svg" alt="Return to Top" width="80px" height="80px">
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

<!-- DEV TOOLS -->
[python]: https://www.python.org/
[pip]: https://pip.pypa.io/en/stable/
[pipx]: https://pipx.pypa.io/stable/
[uv]: https://docs.astral.sh/uv/
[mkdocs]: https://www.mkdocs.org/
[mkdocs.yml]: https://www.mkdocs.org/user-guide/configuration/