<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt
Reflekt enables product & data teams to:
- **Define tracking plans as `code`, encouraging tracking design using software engineering principles** (version control, branches, pull requests, reviews, and CI/CD).
- **Automagically build a dbt package that models and documents the events in a tracking plan** pulled from an Analytics Governance tool, ready for use in a dbt project.

Each Reflekt dbt package includes:
- A dbt [source](https://docs.getdbt.com/docs/building-a-dbt-project/using-sources) pointing to the schema and tables in the warehouse where the raw event data is loaded.
- A dbt [model](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) for each event in the tracking plan. Ready for consumption or use in downstream models.
- A dbt [doc](https://docs.getdbt.com/docs/building-a-dbt-project/documentation) entry for every event modeled in the package. These docs are a perfect *reflektion* of the tracking plan, ensuring the data team and business always know what a model and its columns mean.


https://user-images.githubusercontent.com/28986302/174642373-1208d0d8-b0a9-4b74-94f2-5bcca8073e99.mp4


## Getting Started
Install Reflekt with `pip`.
```bash
pip install reflekt
```

## Documentation
See the **[Reflekt Docs](https://reflekt-ci.notion.site/Reflekt-Docs-a27c2dd7006b4584b6a451819b09cdb7)** site for documentation on setup, commands, configuration, usage, supported integrations, and demos.

## How it works
At a high level:
- Reflekt connects to the tracking plans in your Analytics Governance tool.
- Reflekt knows the Customer Data Platform (CDP) used to collect your first-party data.
- Reflekt connects to your Data Warehouse.

With these connections, Reflekt knows what events and properties you’ve planned while understanding how your CDP collects event data. Pairing this knowledge with the schema, table, and column information pulled from the warehouse, Reflekt can intelligently template dbt models and documentation accordingly.

![reflekt-architecture](/docs/reflekt-arch-flow.jpg)

## Reporting bugs
If you want to report a bug or request a feature, please open an [issue](https://github.com/GClunies/reflekt/issues).

## Contributing code
Contributions are welcome. Feel free to open a [Pull Request](https://github.com/GClunies/reflekt/pulls).

#### Development environment
reflekt uses [poetry](https://python-poetry.org/) for packaging and dependency management. If you use poetry, this repo includes `poetry.lock` and `pyproject.toml` files to help spin up a dev environment.

If you prefer to use another solution (e.g. pipenv, venv, conda) for packaging and dependency management, a `requirements-dev.txt` is included in this repo as well.
