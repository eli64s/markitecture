### Installation

ReadmeAI is available on [PyPI][pypi-link] as readmeai and can be installed as follows:

<!-- #### Using `pip` [![pypi][pypi-shield]][pypi-link] -->

#### ![pip][python-svg]{ width="2%" }&emsp13;Pip

Install with pip (recommended for most users):

```sh
❯ pip install -U readmeai
```

<!-- #### Using `pipx` [![pipx][pipx-shield]][pipx-link] -->

#### ![pipx][pipx-svg]{ width="2%" }&emsp13;Pipx

With `pipx`, readmeai will be installed in an isolated environment:

```sh
❯ pipx install readmeai
```

#### ![uv][uv-svg]{ width="2%" }&emsp13;Uv

The fastest way to install readmeai is with [uv][uv-link]:

```sh
❯ uv tool install readmeai
```

<!-- #### Using `docker` [![docker][docker-shield]][docker-link] -->

#### ![docker][docker-svg]{ width="2%" }&emsp13;Docker

To run `readmeai` in a containerized environment, pull the latest image from [Docker Hub][dockerhub-link]:

```sh
❯ docker pull zeroxeli/readme-ai:latest
```

#### ![build-from-source][git-svg]{ width="2%" }&emsp13;From source

<details><summary><i>Click to build <code>readmeai</code> from source</i></summary>

1. **Clone the repository:**

    ```sh
    ❯ git clone https://github.com/eli64s/readme-ai
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd readme-ai
    ```

3. **Install dependencies:**

    ```sh
    ❯ pip install -r setup/requirements.txt
    ```

Alternatively, use the [setup script][setup-script] to install dependencies:

#### ![bash][bash-svg]{ width="2%" }&emsp13;Bash

1. **Run the setup script:**

    ```sh
    ❯ bash setup/setup.sh
    ```

Or, use `poetry` to build and install project dependencies:

#### ![poetry][poetry-svg]{ width="2%" }&emsp13;Poetry

1. **Install dependencies with poetry:**

    ```sh
    ❯ poetry install
    ```

</details>
<br>

---

<!-- REFERENCE LINKS -->
[bash-svg]: https://raw.githubusercontent.com/eli64s/readme-ai/5ba3f704de2795e32f9fdb67e350caca87975a66/docs/docs/assets/svg/gnubash.svg
[docker-link]: https://hub.docker.com/r/zeroxeli/readme-ai
[docker-shield]: https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white
[docker-svg]: https://raw.githubusercontent.com/eli64s/readme-ai/3052baaca03db99d00808acfec43a44e81ecbf7f/docs/docs/assets/svg/docker.svg
[git-svg]: https://raw.githubusercontent.com/eli64s/readme-ai/5ba3f704de2795e32f9fdb67e350caca87975a66/docs/docs/assets/svg/git.svg
[pipx-link]: https://pipx.pypa.io/stable/
[pipx-shield]: https://img.shields.io/badge/pipx-2CFFAA.svg?style=flat&logo=pipx&logoColor=black
[pipx-svg]: https://raw.githubusercontent.com/eli64s/readme-ai/5ba3f704de2795e32f9fdb67e350caca87975a66/docs/docs/assets/svg/pipx.svg
[poetry-svg]: https://raw.githubusercontent.com/eli64s/readme-ai/5ba3f704de2795e32f9fdb67e350caca87975a66/docs/docs/assets/svg/poetry.svg
[pypi-link]: https://pypi.org/project/readmeai/
[pypi-shield]: https://img.shields.io/badge/PyPI-3775A9.svg?style=flat&logo=PyPI&logoColor=white
[python-svg]: https://raw.githubusercontent.com/eli64s/readme-ai/5ba3f704de2795e32f9fdb67e350caca87975a66/docs/docs/assets/svg/python.svg
[uv-svg]: https://raw.githubusercontent.com/eli64s/readme-ai/5ba3f704de2795e32f9fdb67e350caca87975a66/docs/docs/assets/svg/astral.svg
