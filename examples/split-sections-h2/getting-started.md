## Getting Started

### Prerequisites

ReadmeAI requires Python 3.9 or higher, and one of the following installation methods:

| Requirement                          | Details                          |
|--------------------------------------|----------------------------------|
| • [Python][python-link] ≥3.9         | Core runtime                     |
| **Installation Method** (choose one) |                                  |
| • [pip][pip-link]                    | Default Python package manager   |
| • [pipx][pipx-link]                  | Isolated environment installer   |
| • [uv][uv-link]                      | High-performance package manager |
| • [docker][docker-link]              | Containerized environment        |

### Supported Repository Platforms

To generate a README file, provide the source repository. ReadmeAI supports these platforms:

| Platform                   | Details                   |
|----------------------------|---------------------------|
| [File System][file-system] | Local repository access   |
| [GitHub][github]           | Industry-standard hosting |
| [GitLab][gitlab]           | Full DevOps integration   |
| [Bitbucket][bitbucket]     | Atlassian ecosystem       |

### Supported LLM API Services

ReadmeAI is model agnostic, with support for the following LLM API services:

| Provider                          | Best For        | Details                  |
|-----------------------------------|-----------------|--------------------------|
| [OpenAI][openai]                  | General use     | Industry-leading models  |
| [Anthropic][anthropic]            | Advanced tasks  | Claude language models   |
| [Google Gemini][gemini]           | Multimodal AI   | Latest Google technology |
| [Ollama][ollama]                  | Open source     | No API key needed        |
| [Offline Mode][README-Offline.md] | Local operation | No internet required     |

---

### Installation

ReadmeAI is available on [PyPI][pypi-link] as readmeai and can be installed as follows:

<!-- #### Using `pip` [![pypi][pypi-shield]][pypi-link] -->
<!-- #### ![pip][python-svg]{ width="2%" }&emsp13;Pip -->
#### <img width="2%" src="https://simpleicons.org/icons/python.svg">&emsp13;Pip

Install with pip (recommended for most users):

```sh
❯ pip install -U readmeai
```

<!-- #### Using `pipx` [![pipx][pipx-shield]][pipx-link] -->
<!-- #### ![pipx][pipx-svg]{ width="2%" }&emsp13;Pipx -->
#### <img width="2%" src="https://simpleicons.org/icons/pipx.svg">&emsp13;Pipx

With `pipx`, readmeai will be installed in an isolated environment:

```sh
❯ pipx install readmeai
```

<!-- #### ![uv][uv-svg]{ width="2%" }&emsp13;Uv -->
#### <img width="2%" src="https://simpleicons.org/icons/uv.svg">&emsp13;Uv

The fastest way to install readmeai is with [uv][uv-link]:

```sh
❯ uv tool install readmeai
```

<!-- #### Using `docker` [![docker][docker-shield]][docker-link] -->
<!-- #### ![docker][docker-svg]{ width="2%" }&emsp13;Docker -->
#### <img width="2%" src="https://simpleicons.org/icons/docker.svg">&emsp13;Docker

To run `readmeai` in a containerized environment, pull the latest image from [Docker Hub][dockerhub-link]:

```sh
❯ docker pull zeroxeli/readme-ai:latest
```

<!-- #### ![build-from-source][git-svg]{ width="2%" }&emsp13;From source -->
#### <img width="2%" src="https://simpleicons.org/icons/git.svg">&emsp13;From source

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

<!-- #### ![bash][bash-svg]{ width="2%" }&emsp13;Bash -->
##### <img width="1.5%" src="https://simpleicons.org/icons/gnubash.svg">&emsp13;Bash

1. **Run the setup script:**

    ```sh
    ❯ bash setup/setup.sh
    ```

Or, use `poetry` to build and install project dependencies:

<!-- #### ![poetry][poetry-svg]{ width="2%" }&emsp13;Poetry -->
##### <img width="1.5%" src="https://simpleicons.org/icons/poetry.svg">&emsp13;Poetry

1. **Install dependencies with poetry:**

    ```sh
    ❯ poetry install
    ```

</details>
<br>

### Additional Optional Dependencies

> [!IMPORTANT]
> To use the **Anthropic** and **Google Gemini** clients, extra dependencies are required. Install the package with the following extras:
>
> - **Anthropic:**
>   ```sh
>   ❯ pip install "readmeai[anthropic]"
>   ```
> - **Google Gemini:**
>   ```sh
>   ❯ pip install "readmeai[google-generativeai]"
>   ```
>
> - **Install Multiple Clients:**
>   ```sh
>   ❯ pip install "readmeai[anthropic,google-generativeai]"
>   ```

### Usage

#### Set your API key

When running `readmeai` with a third-party service, you must provide a valid API key. For example, the `OpenAI` client is set as follows:

```sh
❯ export OPENAI_API_KEY=<your_api_key>

# For Windows users:
❯ set OPENAI_API_KEY=<your_api_key>
```

<details closed><summary>Click to view environment variables for - <code>Ollama</code>, <code>Anthropic</code>, <code>Google Gemini</code></summary>
<br>
<details closed><summary>Ollama</summary>
<br>

Refer to the [Ollama documentation][ollama] for more information on setting up the Ollama server.

To start, follow these steps:

1. Pull your model of choice from the Ollama repository:

	```sh
	❯ ollama pull llama3.2:latest
	```

2. Start the Ollama server and set the `OLLAMA_HOST` environment variable:

	```sh
	❯ export OLLAMA_HOST=127.0.0.1 && ollama serve
	```

</details>
<details closed><summary>Anthropic</summary>

1. Export your Anthropic API key:

	```sh
	❯ export ANTHROPIC_API_KEY=<your_api_key>
	```

</details>
<details closed><summary>Google Gemini</summary>

1. Export your Google Gemini API key:

	```sh
	❯ export GOOGLE_API_KEY=<your_api_key
	```

</details>
</details>

#### Using the CLI

##### Running with a LLM API service

Below is the minimal command required to run `readmeai` using the `OpenAI` client:

```sh
❯ readmeai --api openai -o readmeai-openai.md -r https://github.com/eli64s/readme-ai
```

> [!IMPORTANT]
> The default model set is `gpt-3.5-turbo`, offering the best balance between cost and performance.When using any model from the `gpt-4` series and up, please monitor your costs and usage to avoid unexpected charges.

ReadmeAI can easily switch between API providers and models. We can run the same command as above with the `Anthropic` client:
```sh
❯ readmeai --api anthropic -m claude-3-5-sonnet-20240620 -o readmeai-anthropic.md -r https://github.com/eli64s/readme-ai
```

And finally, with the `Google Gemini` client:

```sh
❯ readmeai --api gemini -m gemini-1.5-flash -o readmeai-gemini.md -r https://github.com/eli64s/readme-ai
```

##### Running with local models

We can also run `readmeai` with free and open-source locally hosted models using the Ollama:

```sh
❯ readmeai --api ollama --model llama3.2 -r https://github.com/eli64s/readme-ai
```

##### Running on a local codebase

To generate a README file from a local codebase, simply provide the full path to the project:

```sh
❯ readmeai --repository /users/username/projects/myproject --api openai
```

Adding more customization options:

```sh
❯ readmeai --repository https://github.com/eli64s/readme-ai \
           --output readmeai.md \
           --api openai \
           --model gpt-4 \
           --badge-color A931EC \
           --badge-style flat-square \
           --header-style compact \
           --navigation-style fold \
           --temperature 0.9 \
           --tree-depth 2
           --logo LLM \
           --emojis solar
```

##### Running in offline mode

ReadmeAI supports `offline mode`, allowing you to generate README files without using a LLM API service.

```sh
❯ readmeai --api offline -o readmeai-offline.md -r https://github.com/eli64s/readme-ai
```

<!-- #### ![docker][docker-svg]{ width="2%" }&emsp13;Docker -->
#### <img width="2%" src="https://simpleicons.org/icons/docker.svg">&emsp13;Docker

Run the `readmeai` CLI in a Docker container:

```sh
❯ docker run -it --rm \
    -e OPENAI_API_KEY=$OPENAI_API_KEY \
    -v "$(pwd)":/app zeroxeli/readme-ai:latest \
    --repository https://github.com/eli64s/readme-ai \
    --api openai
```

<!-- #### ![streamlit][streamlit-svg]{ width="2%" }&emsp13;Streamlit -->
#### <img width="2%" src="https://simpleicons.org/icons/streamlit.svg">&emsp13;Streamlit

Try readme-ai directly in your browser on Streamlit Cloud, no installation required.

[<img align="center" src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" width="20%">](https://readme-ai.streamlit.app/)

See the [readme-ai-streamlit][readme-ai-streamlit] repository on GitHub for more details about the application.

> [!WARNING]
> The readme-ai Streamlit web app may not always be up-to-date with the latest features. Please use the command-line interface (CLI) for the most recent functionality.

<!-- #### ![build-from-source][git-svg]{ width="2%" }&emsp13;From source -->
#### <img width="2%" src="https://simpleicons.org/icons/git.svg">&emsp13;From source

<details><summary><i>Click to run <code>readmeai</code> from source</i></summary>

<!-- #### ![bash][bash-svg]{ width="2%" }&emsp13;Bash -->
##### <img width="1.5%" src="https://simpleicons.org/icons/gnubash.svg">&emsp13;Bash

If you installed the project from source with the bash script, run the following command:

1. Activate the virtual environment:

   ```sh
   ❯ conda activate readmeai
   ```

2. Run the CLI:

   ```sh
   ❯ python3 -m readmeai.cli.main -r https://github.com/eli64s/readme-ai
	```

<!-- #### ![poetry][poetry-svg]{ width="2%" }&emsp13;Poetry -->
##### <img width="1.5%" src="https://simpleicons.org/icons/poetry.svg">&emsp13;Poetry

1. Activate the virtual environment:

   ```sh
   ❯ poetry shell
   ```

2. Run the CLI:

   ```sh
   ❯ poetry run python3 -m readmeai.cli.main -r https://github.com/eli64s/readme-ai
   ```

</details>

<img src="https://raw.githubusercontent.com/eli64s/readme-ai/eb2a0b4778c633911303f3c00f87874f398b5180/docs/docs/assets/svg/line-gradient.svg" alt="line break" width="100%" height="3px">

### Testing

<!-- #### Using `pytest` [![pytest][pytest-shield]][pytest-link] -->

The [pytest][pytest-link] and [nox][nox-link] frameworks are used for development and testing.

Install the dependencies with uv:

```sh
❯ uv pip install --dev --group test --all-extras
```

Run the unit test suite using Pytest:

```sh
❯ make test
```

Using nox, test the app against Python versions `3.9`, `3.10`, `3.11`, and `3.12`:

```sh
❯ make test-nox
```

> [!TIP]
> <sub>Nox is an automation tool for testing applications in multiple environments. This helps ensure your project is compatible with across Python versions and environments.</sub>

<img src="https://raw.githubusercontent.com/eli64s/readme-ai/eb2a0b4778c633911303f3c00f87874f398b5180/docs/docs/assets/svg/line-gradient.svg" alt="line break" width="100%" height="3px">

---

<!-- REFERENCE LINKS -->
[README-Offline.md]: https://github.com/eli64s/readme-ai/blob/main/examples/offline-mode/readme-litellm.md
[anthropic]: https://docs.anthropic.com/en/home
[bash-svg]: https://simpleicons.org/icons/gnubash.svg
[bitbucket]: https://bitbucket.org/
[docker-link]: https://hub.docker.com/r/zeroxeli/readme-ai
[docker-shield]: https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white
[docker-svg]: https://simpleicons.org/icons/docker.svg
[file-system]: https://en.wikipedia.org/wiki/File_system
[gemini]: https://ai.google.dev/tutorials/python_quickstart
[git-svg]: https://simpleicons.org/icons/git.svg
[github]: https://github.com/
[gitlab]: https://gitlab.com/
[nox-link]: https://nox.thea.codes/en/stable/
[ollama]: https://github.com/ollama/ollama
[openai]: https://platform.openai.com/docs/quickstart/account-setup:
[pip-link]: https://pip.pypa.io/en/stable/
[pipx-link]: https://pipx.pypa.io/stable/
[pipx-shield]: https://img.shields.io/badge/pipx-2CFFAA.svg?style=flat&logo=pipx&logoColor=black
[pipx-svg]: https://simpleicons.org/icons/pipx.svg
[poetry-svg]: https://simpleicons.org/icons/poetry.svg
[pypi-link]: https://pypi.org/project/readmeai/
[pypi-shield]: https://img.shields.io/badge/PyPI-3775A9.svg?style=flat&logo=PyPI&logoColor=white
[pytest-link]: https://docs.pytest.org/en/7.1.x/contents.html
[pytest-shield]: https://img.shields.io/badge/Pytest-0A9EDC.svg?style=flat&logo=Pytest&logoColor=white
[python-link]: https://www.python.org/
[python-svg]: https://simpleicons.org/icons/python.svg
[readme-ai-streamlit]: https://github.com/eli64s/readme-ai-streamlit
[streamlit-svg]: https://simpleicons.org/icons/streamlit.svg
[uv-link]: https://docs.astral.sh/uv/
[uv-svg]: https://simpleicons.org/icons/astral.svg
