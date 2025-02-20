<div id="top" align="center">

<!-- HEADER -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/eli64s/markitecture/13c4b28213fb8e8c75299ef5c905ce1d195a6988/docs/assets/logos/circle-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/eli64s/markitecture/13c4b28213fb8e8c75299ef5c905ce1d195a6988/docs/assets/logos/circle-light.svg">
  <img alt="markitecture Logo" src="https://raw.githubusercontent.com/eli64s/markitecture/13c4b28213fb8e8c75299ef5c905ce1d195a6988/docs/assets/logos/circle-light.svg" width="900" style="max-width: 100%;">
</picture>

<h3 align="center">
   Building Blocks for Brilliant Documentation.
</h3>
<p align="center">
  <em>Markitecture: The Python toolkit that empowers modular Markdown workflows.</em>
</p>

<!-- BADGES -->
<div align="center">
  <p align="center" style="margin-bottom: 20px;">
    <a href="https://github.com/eli64s/markitecture/actions">
      <img src="https://img.shields.io/github/actions/workflow/status/eli64s/markitecture/ci.yml?label=CI&style=flat&logo=githubactions&logoColor=white&labelColor=2A2A2A&color=FFD700" alt="GitHub Actions" />
    </a>
    <a href="https://app.codecov.io/gh/eli64s/markitecture">
      <img src="https://img.shields.io/codecov/c/github/eli64s/markitecture?label=Coverage&style=flat&logo=codecov&logoColor=white&labelColor=2A2A2A&color=3fe1c0" alt="Coverage" />
    </a>
    <a href="https://pypi.org/project/markitecture/">
      <img src="https://img.shields.io/pypi/v/markitecture?label=PyPI&style=flat&logo=pypi&logoColor=white&labelColor=2A2A2A&color=00E5FF" alt="PyPI Version" />
    </a>
    <a href="https://github.com/eli64s/markitecture">
      <img src="https://img.shields.io/pypi/pyversions/markitecture?label=Python&style=flat&logo=python&logoColor=white&labelColor=2A2A2A&color=7934C5" alt="Python Version" />
    </a>
    <a href="https://opensource.org/license/mit/">
      <img src="https://img.shields.io/github/license/eli64s/markitecture?label=License&style=flat&logo=opensourceinitiative&logoColor=white&labelColor=2A2A2A&color=FF00FF" alt="MIT License">
    </a>
  </p>
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/eli64s/markitecture/216a92894e6f30c707a214fad5a5fba417e3bc39/docs/assets/line.svg" alt="separator" width="100%" height="2px" style="margin: 20px 0;">
</div>

</div>
<!-- HEADER END -->

## What is Markitecture?

**Markitecture** is a comprehensive Python toolkit designed to streamline your Markdown workflow. Whether you're managing documentation, writing technical content, or maintaining a knowledge base, Markitecture provides essential utilities to make working with Markdown files easier and more efficient.

### Key Features

- **Text Splitting:** Break down large Markdown files into manageable sections based on headings or custom rules.
- **Link Management:** Convert between inline and reference-style links, validate URLs, and identify broken links.
- **Content Analysis:** Analyze document structure, extract metadata, and ensure consistent formatting.
- **Documentation Tools:** Generate configurations for static site generators like [MkDocs][mkdocs].

---

## Quick Start

### Installation

Install from [PyPI][pypi] using your preferred package manager.

#### <img width="2%" src="https://simpleicons.org/icons/python.svg">&emsp13;pip

Use [pip][pip] (recommended for most users):

```sh
pip install -U markitecture
```

#### <img width="2%" src="https://simpleicons.org/icons/pipx.svg">&emsp13;pipx

Install in an isolated environment with [pipx][pipx]:

```sh
❯ pipx install markitecture
```

#### <img width="2%" src="https://simpleicons.org/icons/uv.svg">&emsp13;uv

For the fastest installation use [uv][uv]:

```sh
❯ uv tool install markitecture
```

### Using the CLI

#### Text Splitting

Split large Markdown files into smaller, organized sections:

```sh
markitect \
    --split.i tests/data/readme-ai.md \
    --split.o examples/split-sections-h2
```

#### Link Validation

Check for broken links in your documentation:

```sh
markitect --check-links.input tests/data/pydantic.md
```

In your terminal, you'll see a summary of the results:

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

In Markdown, [reference-style links][reflinks] let you write cleaner text by keeping URLs in a reference section - think footnotes for the web.

To convert inline links to reference-style links:

```sh
markitect \
    --reflinks.input tests/data/pydantic.md \
    --reflinks.output with_refs.md
```

#### Static Site Configuration Generation

Generate a MkDocs configuration [(mkdocs.yml)][mkdocs.yml] from a given Markdown file.

1. Split the Markdown file into sections:

    ```sh
    markitect \
        --split.i tests/data/readme-ai.md \
        --split.o examples/split-sections-h2
    ```

2. Generate the MkDocs configuration:

    ```sh
    markitect \
        --mkdocs.dir examples/split-sections-h2 \
        --mkdocs.site-name "MyDocsSite"
    ```

<sub>

See additional example and usage details in the [here][examples].

</sub>

<!--
>[!NOTE]
> Explore the [Official Documentation][docs] for more detailed guides and examples.
-->

---

## Roadmap

- [ ] Support for additional documentation formats (e.g., reStructuredText, HTML)
- [ ] Enhanced link management utilities
- [ ] Improved content analysis features
- [ ] Integration with more static site generators
- [ ] Plugin system for custom utilities
- [ ] More intuitive CLI commands and options

---

## Contributing

Contributions are welcome! Whether it's bug reports, feature requests, or code contributions, please feel free to:

- Open an [issue][github-issues]
- Submit a [pull request][github-pulls]
- Improve documentation, write tutorials, etc.
- Share your feedback and suggestions

---

## License

Copyright © 2024-2025 [Markitecture][markitecture]. <br />
Released under the [MIT][mit-license] license.

<div align="left">
  <a href="#top">
    <img src="https://raw.githubusercontent.com/eli64s/markitecture/77bec69129dd3a075d7d0816c7bd826da131ccc7/docs/assets/buttons/rectangle.svg" width="100px" height="100px" alt="Return to Top">
  </a>
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/eli64s/markitecture/216a92894e6f30c707a214fad5a5fba417e3bc39/docs/assets/line.svg" alt="separator" width="100%" height="2px" style="margin: 20px 0;">
</div>


<!-- REFERENCE LINKS -->

<!-- PROJECT RESOURCES -->
[pypi]: https://pypi.org/project/markitecture/
[markitecture]: https://github.com/eli64s/markitecture
[github-issues]: https://github.com/eli64s/markitecture/issues
[github-pulls]: https://github.com/eli64s/markitecture/pulls
[mit-license]: https://github.com/eli64s/markitecture/blob/main/LICENSE
[examples]: https://github.com/eli64s/markitecture/tree/main/examples

<!-- DEVELOPER TOOLS -->
[python]: https://www.python.org/
[pip]: https://pip.pypa.io/en/stable/
[pipx]: https://pipx.pypa.io/stable/
[uv]: https://docs.astral.sh/uv/
[mkdocs]: https://www.mkdocs.org/
[mkdocs.yml]: https://www.mkdocs.org/user-guide/configuration/

<!-- RESOURCES -->
[reflinks]: https://www.markdownguide.org/basic-syntax/#reference-style-links
