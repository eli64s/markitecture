<div id="top">

<div align="center">
  
<img src="docs/assets/logo.svg" alt="splitme-ai" width="100%" height="100%" />

__Markdown Splitter: Modular Docs, Maximum Flexibility__

</div>

`SplitmeAI` is a Python module that addresses challenges in managing large Markdown files, particularly when creating and maintaining structured static documentation websites such as [Mkdocs][mkdocs].

__Why Use SplitmeAI?__

- **Section Splitting:** Breaks down large Markdown files into smaller, manageable sections based on specified heading levels.
- **Filename Sanitization:** Generates clean, unique filenames for each section, ensuring compatibility and readability.
- **Reference Link Management:** Extracts and appends reference-style links used within each section.
- **Hierarchy Preservation:** Maintains parent heading context within each split file.
- **Thematic Break Handling:** Recognizes and handles line breaks (`---`, `***`, `___`) for intelligent content segmentation.
- **MkDocs Integration:** Automatically generates an `mkdocs.yml` configuration file based on the split sections.
- **CLI Support:** Provides a user-friendly Command-Line Interface for seamless operation.

</div>

<img src="docs/assets/line.svg" alt="---" width="100%" height="3.5px">

## Quick Start

### Installation

Install from [PyPI][pypi] using any of the package managers listed below.

#### ![pip][python-svg]{width="2%"} &emsp13;Pip

Use [pip][pip] (recommended for most users):

```sh
pip install -U splitme-ai
```

#### ![pipx][pipx-svg]{ width="2%" }&emsp13;Pipx

Install in an isolated environment with [pipx][pipx]:

```sh
❯ pipx install readmeai
```

#### ![uv][uv-svg]{ width="2%" }&emsp13;Uv

For the fastest installation use [uv][uv]:

```sh
❯ uv tool install splitme
```

### Usage

#### Using the CLI

__Example 1:__ Split a Markdown file into sections:

```sh
splitme-ai \
    --split.i examples/data/README-AI.md \
    --split.settings.o examples/output-h2
```

__Example 2:__ Generate a mkdocs static documentation site config file:

```sh
splitme-ai \
    --split.i examples/data/README-AI.md \
    --split.settings.o examples/output-h2 \
    --split.settings.mkdocs
```

View the output for [heading level 2 example here](./examples/output-h2).

__Example 3:__ Split on heading level 3:

```sh
splitme-ai \
    --split.i examples/data/README-AI.md \
    --split.settings.o examples/output-h3 \
    --split.settings.hl "###"
```

View the output for [heading level 3 example here](./examples/output-h3).

__Example 4:__ Split on heading level 4:

```sh
splitme-ai \
    --split.i examples/data/README-AI.md \
    --split.settings.o examples/output-h4 \
    --split.settings.hl "####"
```

View the output for [heading level 4 example here](./examples/output-h4).

>[!NOTE]
> The Official Documentation site with extensive examples and usage instructions is under development Stay tuned for updates!

## Roadmap

- [ ] Enhance CLI usability and user experience.
- [ ] Integrate AI-powered content analysis and segmentation.
- [ ] Add robust chunking and splitting algorithms for LLM applications.
- [ ] Add support for additional static site generators.
- [ ] Add support for additional input and output formats.

## License

This project is licensed under the terms of the MIT License.

<div align="left">
  <a href="#top">
    <img src="docs/assets/button-circles.svg" alt="Return" width="100px" height="100px">
  </a>
</div>

<img src="docs/assets/line.svg" alt="---" width="100%" height="3.5px">

<!-- REFERENCE LINKS -->

<!-- QUICK START -->
[pypi]: https://pypi.org/project/splitme-ai/
[docker]: https://hub.docker.com/r/zeroxeli/splitme-ai
[pip]: https://pip.pypa.io/en/stable/
[pipx]: https://pipx.pypa.io/stable/
[python]: https://www.python.org/
[uv]: https://docs.astral.sh/uv/
[mkdocs]: https://www.mkdocs.org/

<!-- SHIELDS -->
[docker-shield]: https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white
[pipx-shield]: https://img.shields.io/badge/pipx-2CFFAA.svg?style=flat&logo=pipx&logoColor=black
[pypi-shield]: https://img.shields.io/badge/PyPI-3775A9.svg?style=flat&logo=PyPI&logoColor=white
[pytest-shield]: https://img.shields.io/badge/Pytest-0A9EDC.svg?style=flat&logo=Pytest&logoColor=white

<!-- SVG ICONS -->
[pipx-svg]: https://raw.githubusercontent.com/eli64s/readme-ai/5ba3f704de2795e32f9fdb67e350caca87975a66/docs/docs/assets/svg/pipx.svg
[python-svg]: https://raw.githubusercontent.com/eli64s/readme-ai/5ba3f704de2795e32f9fdb67e350caca87975a66/docs/docs/assets/svg/python.svg
[uv-svg]: https://raw.githubusercontent.com/eli64s/readme-ai/5ba3f704de2795e32f9fdb67e350caca87975a66/docs/docs/assets/svg/astral.svg
