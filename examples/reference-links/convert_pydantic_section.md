# Pydantic
![[CI][ci]](https://github.com/pydantic/pydantic/actions?query=event%3Apush+branch%3Amain+workflow%3ACI)
![[Coverage][coverage]](https://coverage-badge.samuelcolvin.workers.dev/redirect/pydantic/pydantic)
![[pypi][pypi]](https://pypi.python.org/pypi/pydantic)
![[CondaForge][condaforge]](https://anaconda.org/conda-forge/pydantic)
![[downloads][downloads]](https://pepy.tech/project/pydantic)
![[versions][versions]](https://github.com/pydantic/pydantic)
![[license][license]](https://github.com/pydantic/pydantic/blob/main/LICENSE)
![[Pydantic v2][pydantic-v2]](https://docs.pydantic.dev/latest/contributing/#badges)

Data validation using Python type hints.

Fast and extensible, Pydantic plays nicely with your linters/IDE/brain.
Define how data should be in pure, canonical Python 3.8+; validate it with Pydantic.

<!-- PYDANTIC REFERENCE LINKS -->
[ci]: https://img.shields.io/github/actions/workflow/status/pydantic/pydantic/ci.yml?branch=main&logo=github&label=CI
[condaforge]: https://img.shields.io/conda/v/conda-forge/pydantic.svg
[coverage]: https://coverage-badge.samuelcolvin.workers.dev/pydantic/pydantic.svg
[downloads]: https://static.pepy.tech/badge/pydantic/month
[license]: https://img.shields.io/github/license/pydantic/pydantic.svg
[pydantic-v2]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json
[pypi]: https://img.shields.io/pypi/v/pydantic.svg
[versions]: https://img.shields.io/pypi/pyversions/pydantic.svg

---

## Pydantic Logfire :fire:

We've recently launched Pydantic Logfire to help you monitor your applications. [Learn more][learn-more]

<!-- PYDANTIC LOGFIRE :FIRE: REFERENCE LINKS -->
[learn-more]: https://pydantic.dev/articles/logfire-announcement

---

## Pydantic V1.10 vs. V2

Pydantic V2 is a ground-up rewrite that offers many new features, performance improvements, and some breaking changes compared to Pydantic V1.

If you're using Pydantic V1 you may want to look at the [pydantic V1.10 Documentation][pydantic-v110-documentation] or, [`1.10.X-fixes` git branch][110x-fixes-git-branch]. Pydantic V2 also ships with the latest version of Pydantic V1 built in so that you can incrementally upgrade your code base and projects: `from pydantic import v1 as pydantic_v1`.

<!-- PYDANTIC V1.10 VS. V2 REFERENCE LINKS -->
[110x-fixes-git-branch]: https://github.com/pydantic/pydantic/tree/1.10.X-fixes
[pydantic-v110-documentation]: https://docs.pydantic.dev/

---

## Help

See [documentation][documentation] for more details.

<!-- HELP REFERENCE LINKS -->
[documentation]: https://docs.pydantic.dev/

---

## Installation

Install using `pip install -U pydantic` or `conda install pydantic -c conda-forge`.
For more installation options to make Pydantic even faster,
see the [Install][install] section in the documentation.

<!-- INSTALLATION REFERENCE LINKS -->
[install]: https://docs.pydantic.dev/install/invalid-link

---

## A Simple Example

```python
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str = 'John Doe'
    signup_ts: Optional[datetime] = None
    friends: List[int] = []

external_data = {'id': '123', 'signup_ts': '2017-06-01 12:22', 'friends': [1, '2', b'3']}
user = User(**external_data)
print(user)
#> User id=123 name='John Doe' signup_ts=datetime.datetime(2017, 6, 1, 12, 22) friends=[1, 2, 3]
print(user.id)
#> 123
```
