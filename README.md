<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt
Reflekt enables Data, Engineering, and Product teams to:
- Define tracking plans as `code` (see [supported tracking plans](https://www.notion.so/reflekt-ci/Reflekt-Docs-a27c2dd7006b4584b6a451819b09cdb7#725dd17834dd4f13b5966c6cbf4e5369)).
- Manage and update tracking plans using version control and CI/CD.
- Automagically build a dbt package that models the data for tracking plan events for use in a dbt project. Reflekt dbt packages include:
  - dbt [sources](https://docs.getdbt.com/docs/building-a-dbt-project/using-sources) pointing to the schema and table in the warehouse where the raw event data is loaded.
  - dbt [models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) for each event in the tracking plan.
  - dbt [docs](https://docs.getdbt.com/docs/building-a-dbt-project/documentation) for every modeled event that *reflekt* the context in the tracking plan.

**Product analytics is a team sport.** With Reflekt:
-  Product & Data teams can plan what they want to track.
-  Engineering teams have clear contracts to guide and validate event instrumentation.
-  Data teams can build and maintain models and docs that *reflekt* the latest product analytics events in a fraction of the time.


https://user-images.githubusercontent.com/28986302/174643122-a38ef58b-bf98-451c-b9da-09d3554794b2.mp4


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

With these connections, Reflekt knows what events and properties you’ve planned while understanding how your CDP collects event data. Pairing this knowledge with schema, table, and column information pulled from the warehouse, Reflekt can intelligently template dbt models and documentation accordingly.

![reflekt-architecture](/docs/reflekt-arch-flow.jpg)

## Reporting bugs
If you want to report a bug or request a feature, please open an [issue](https://github.com/GClunies/reflekt/issues).

## Contributing code
Contributions are welcome. Feel free to open a [Pull Request](https://github.com/GClunies/reflekt/pulls).

#### Development environment
Reflekt uses [poetry](https://python-poetry.org/) for packaging and dependency management. If you use poetry, this repo includes `poetry.lock` and `pyproject.toml` files to help spin up a dev environment.

If you prefer to use another solution (e.g. pipenv, venv, conda) for packaging and dependency management, a `requirements-dev.txt` is included in this repo as well.
