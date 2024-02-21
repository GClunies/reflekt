<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt
> /rəˈflek(t)/ - _to embody or represent in a faithful or appropriate way_

![PyPI](https://img.shields.io/pypi/v/reflekt?style=for-the-badge)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/reflekt?style=for-the-badge)
![GitHub](https://img.shields.io/github/license/gclunies/reflekt?style=for-the-badge)

Reflekt helps teams design, govern, and model event data for warehouse-first product analytics. Events schemas are designed and codified using [JSON schema](https://json-schema.org/), version controlled in a Reflekt project, and updated via pull requests (PRs), enabling:
  - Branches for parallel development and testing.
  - Reviews and discussion amongst teams and stakeholders.
  - CI/CD suites to:
    - `reflekt lint` schemas against naming and metadata rules.
    - `reflekt push` schemas to deploy them to a [schema registry](#schema-registry) for event data validation.

With codified event schemas and a data warehouse connection, Reflekt can model, document, and test event data in dbt ✨automagically✨...
[![asciicast](https://asciinema.org/a/OEXbTtj0U0KL7bZo5Ea7ngNnh.svg)](https://asciinema.org/a/OEXbTtj0U0KL7bZo5Ea7ngNnh)

## Features


## Installation


## Contribute
- Source Code: [github.com/GClunies/reflekt](https://github.com/GClunies/reflekt)
- Issue Tracker: [github.com/GClunies/reflekt/issues](https://github.com/GClunies/reflekt/issues)
- Pull Requests: [github.com/GClunies/reflekt/pulls](https://github.com/GClunies/reflekt/pulls)

## License
This project is [licensed](LICENSE) under the Apache-2.0 License.

> [!NOTE]
> Reflekt uses `reuse` to attribute licenses for every line of code, recognizing the work of others and ensuring compliance with the licenses of any software used.
