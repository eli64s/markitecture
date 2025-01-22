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
[nox-link]: https://nox.thea.codes/en/stable/
[pytest-link]: https://docs.pytest.org/en/7.1.x/contents.html
[pytest-shield]: https://img.shields.io/badge/Pytest-0A9EDC.svg?style=flat&logo=Pytest&logoColor=white
