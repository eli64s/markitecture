### Testing

<!-- #### Using `pytest` [![pytest][pytest-shield]][pytest-link] -->

The [pytest][pytest-link] and [nox][nox-link] frameworks are used for development and testing.

Install the dependencies with uv:

```sh
❯ uv pip install -r pyproject.toml --all-extras
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

<img src="readmeai/data/svg/gradient_line_4169E1_8A2BE2.svg" alt="line break" width="100%" height="3px">

---

<!-- REFERENCE LINKS -->
[nox-link]: https://nox.thea.codes/en/stable/
[pytest-link]: https://docs.pytest.org/en/7.1.x/contents.html
[pytest-shield]: https://img.shields.io/badge/Pytest-0A9EDC.svg?style=flat&logo=Pytest&logoColor=white
