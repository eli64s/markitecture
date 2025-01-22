### Generated Sections & Content

<details><summary><strong>꩜ Expand to view more!</strong></summary><br>

| <h3>Project Introduction</h3> <ul><li>This section captures your project's essence and value proposition. </li><li>The prompt template used to generate this section can be viewed [here][prompts.toml]. </li></ul> |
| :--- |
| ![][project-overview] |

| <h3>Features Table</h3> <ul><li>Detailed feature breakdown and technical capabilities. </li><li> The prompt template used to generate this section can be viewed [here][prompts.toml]. </li></ul> |
| :--- |
| ![][features-table] |

| <h3>Project Structure</h3> <ul><li>Visual representation of your project's directory structure. </li><li>The tree is generated using [pure Python][tree.py] and embedded in a code block. </li></ul> |
| :--- |
| ![][project-structure] |
| <h3>Project Index</h3> <ul><li>Summarizes key modules of the project, which are also used as context for downstream [prompts.toml][prompts.toml]. </li></ul> |
| ![][project-index] |

| <h3>Getting Started Guides</h3> <ul><li>Dependencies and system requirements are extracted from the codebase during preprocessing. </li><li>The [parsers][readmeai.parsers] handle most of the heavy lifting here. </li></ul> |
| :--- |
| ![][installation-steps] |
| <h3>Installation, Usage, & Testing</h3> <ul><li>Setup instructions and usage guides are automatically created based on data extracted from the codebase. </li></ul> |
| ![][usage-guides] |

| <h3>Community & Support</h3> <ul><li>Development roadmap, contribution guidelines, license information, and community resources. </li><li>A <em>return button</em> is also included for easy navigation. </li></ul> |
| :--- |
| ![][community-and-support] |
| <h3>Contribution Guides</h3> <ul><li>Instructions for contributing to the project, including resource links and a basic contribution guide. </li><li>Graph of contributors is also included for open-source projects. </li></ul> |
| ![][contributing-guidelines] |

</details>

<img src="https://raw.githubusercontent.com/eli64s/readme-ai/eb2a0b4778c633911303f3c00f87874f398b5180/docs/docs/assets/svg/line-gradient.svg" alt="line break" width="100%" height="3px">

---

<!-- REFERENCE LINKS -->
[community-and-support]: https://github.com/eli64s/readme-ai/blob/main/docs/docs/assets/img/community/community-and-support.png?raw=true
[contributing-guidelines]: https://github.com/eli64s/readme-ai/blob/main/docs/docs/assets/img/community/contributing-guidelines.png?raw=true
[features-table]: https://github.com/eli64s/readme-ai/blob/main/docs/docs/assets/img/features/features.png?raw=true
[installation-steps]: https://github.com/eli64s/readme-ai/blob/main/docs/docs/assets/img/getting-started/installation-steps.png?raw=true
[project-index]: https://github.com/eli64s/readme-ai/blob/main/docs/docs/assets/img/project-structure/project-index.png?raw=true
[project-overview]: https://github.com/eli64s/readme-ai/blob/main/docs/docs/assets/img/project-overview/introduction.png?raw=true
[project-structure]: https://github.com/eli64s/readme-ai/blob/main/docs/docs/assets/img/project-structure/project-structure.png?raw=true
[prompts.toml]: https://github.com/eli64s/readme-ai/blob/main/readmeai/config/settings/prompts.toml
[readmeai.parsers]: https://github.com/eli64s/readme-ai/tree/main/readmeai/parsers
[tree.py]: https://github.com/eli64s/readme-ai/blob/main/readmeai/generators/tree.py
[usage-guides]: https://github.com/eli64s/readme-ai/blob/main/docs/docs/assets/img/getting-started/usage-guides.png?raw=true
