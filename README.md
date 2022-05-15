<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt
**Reflekt is a command line interface and continuous integration tool for your tracking plan.** It integrates with your Analytics Governance Tool, Customer Data Platform (CDP), data warehouse, and [dbt](https://www.getdbt.com/).

![reflekt-arch](/docs/reflekt_architecture.png)

Reflekt defines tracking plans as `code`, powering its **dbt package templater** to write dbt packages modeling **all the events in your tracking plan**.

Every Reflekt dbt package includes:
- dbt [sources](https://docs.getdbt.com/docs/building-a-dbt-project/using-sources) pointing to the schema and tables in your warehouse where the raw event data is stored.
- dbt [models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) for every event in your tracking plan. Reflekt does light transformations so these models are are ready for consumption or further modeling.
- dbt [documentation](https://docs.getdbt.com/docs/building-a-dbt-project/documentation) for every model in the package. Your analysts and the business always know what your tables and columns mean.
## [DEMO VIDEO HERE]

## Why Reflekt?
- Bet on a warehouse-first approach to product analytics.
- Your tracking plans is upstream of all products analytics, including dbt. We need great tools to codify these plans and distribute their definition throughout the stack.
- Your dbt models & docs should perfectly *reflekt* the events specified in your tracking plan.
- Tracking plan development should *reflekt* software development flows. Branching, version control, ability to roll-back.
- The context and information in your tracking plan should be available in the
- Your tracking plans should be *extensible*.
- You should own the tracking plan in your repo.

## Getting started
- [Install & Setup](docs/INSTALL-SETUP.md)
- [Tracking plans as code](docs/TRACKING-PLANS-AS-CODE.md)
- [Reflekt commands](docs/COMMANDS.md)
- [Integrations](docs/INTEGRATIONS.md) (Analytics Governance Tools, CDPs, warehouses)

## Reporting bugs
If you want to report a bug or request a feature, please open an [issue](https://github.com/GClunies/reflekt/issues).

## Contributing code
Please feel free to open a [Pull Request](https://github.com/GClunies/reflekt/pulls) for contributions you would like to propose. Please see the [contributing](docs/CONTRIBUTING-CODE.md) docs for development environment details and guidance.
