# Contributing to Markitecture

👋 Welcome, thank you for considering contributing to Markitecture! Happy to have you join our community. Every contribution, no matter how small, helps make Markitecture better for everyone.

This document outlines how to contribute to the project and the standards we follow. Please take a few moments to read through it before submitting your first contribution.

## How You Can Contribute

There are many ways you can contribute to Markitecture:

*   **🐛 Report Bugs:** Found a bug? Let us know by opening a [new issue][issues]. Please provide a clear description of the issue, including steps to reproduce it, your operating system, Python version, and Markitecture version.
*   **✨ Suggest Enhancements:** Have an idea for a new feature or improvement? We'd love to hear it! Open a [new issue][issues] and describe your suggestion.
*   **📖 Improve Documentation:** Help us make the documentation clearer, more comprehensive, or more accurate.
*   **🛠️ Contribute Code:** Contribute new features, fix bugs, or improve existing code.
*   **📣 Spread the Word:** Share Markitecture with others who might find it useful!

## Getting Started

Here's how to get started with contributing code or documentation:

1.  **Fork the Repository:** Start by forking the [Markitecture repository][markitecture] on GitHub (or your chosen platform).

2.  **Clone Your Fork:** Clone your forked repository to your local machine:

    ```bash
    git clone https://github.com/eli64s/markitecture.git
    cd markitecture
    ```

3.  **Create a Branch:** Create a new branch for your changes:

    ```bash
    git checkout -b feature/your-feature-name
    ```

    Use a descriptive branch name that reflects your changes (e.g., `bugfix/link-validation-edge-case`, `feature/new-feature`, `docs/update-readme`). This will help you and others easily identify the purpose of the branch.

4.  **Set Up Your Development Environment:**

    Follow these steps to get a development version of Markitecture up and running:

    1.  **Create a virtual environment:**

        ```bash
        make venv
        ```

    2.  **Install project dependencies:**

        ```bash
        make install
        make lock
        ```

    3.  **Install pre-commit hooks:**

        ```bash
        pre-commit install
        ```

5.  **Make Your Changes:** Implement your bug fix, feature, or documentation update.

6.  **Test Your Changes:** Ensure your changes don't break existing functionality by running the tests:

    ```bash
    make test
    ```

7.  **Commit Your Changes:** Commit your changes with clear and concise commit messages:

    ```bash
    git commit -m "fix: Resolved issue with link validation"
    ```

8.  **Push to Your Fork:** Push your branch to your forked repository:

    ```bash
    git push origin feature/your-feature-name
    ```

9.  **Open a Pull Request:** Go to the original Markitecture repository and open a pull request from your branch. Provide a clear description of your changes in the pull request.

## Code Style and Standards

*   We adhere to the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code.
*   We use `ruff` for code formatting and linting. You can run it locally before committing:

    ```bash
    make format-and-lint
    ```
*   Add tests for any new features or bug fixes.
*   Document any new or changed functionality in the code using docstrings and, if necessary, update the user-facing documentation.
*   Keep your code clean, well-commented, and easy to understand.

## Code of Conduct

We expect all contributors to follow our [Code of Conduct]([link to your Code of Conduct - e.g., CODE_OF_CONDUCT.md]). Please be respectful and considerate of others in all your interactions within the project.

## Pull Request Process

1.  We'll review your pull request as soon as possible.
2.  We may suggest changes or improvements. We encourage open feedback and collaboration.
3.  Once your pull request is approved, it will be merged into the `main` branch.

## Questions and Support

If you have any questions or need help with contributing, please don't hesitate to:

*   Open an [issue][issues] in the project's issue tracker.
*   Join our [discussion forum][discussions] and ask your question there.

We appreciate your contributions and look forward to collaborating with you!

---

**Cheers!**

The Markitecture Team

<!-- REFERENCE LINKS -->
[discussions]: https://github.com/eli64s/markitecture/discussions
[issues]: https://github.com/eli64s/markitecture/issues
[markitecture]: https://github.com/eli64s/markitecture/
