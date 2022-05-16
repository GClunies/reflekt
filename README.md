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
- dbt [documentation](https://docs.getdbt.com/docs/building-a-dbt-project/documentation) for every model in the package. dbt models and docs perfectly *reflekt* the events in the tracking plan. Analysts and the business always know what your tables and columns mean.
## DEMO VIDEO HERE

## Getting started
- [Install & Setup](docs/INSTALL-SETUP.md)
- [Tracking plan as code](docs/TRACKING-PLANS-AS-CODE.md)
- [Commands](docs/COMMANDS.md)
- [Integrations](docs/INTEGRATIONS.md) (Analytics Governance Tools, CDPs, warehouses)

## Beliefs & Bets
The core belief of Reflekt is **Tracking plans are the most important artifact in a product analytics stack.** Everything a team builds, collects, and uses - application tracking code, event validation, raw data, dbt models & docs, analyses -  are all dependent on the plan. Tracking plans should be defined as `code` and Tracking plan development should *reflekt* software development. Tracking plans should:
  - Be version controlled, with branches and environments for different development stages (i.e. dev/staging/prod).
  - Leverage continuous integration to test and deploy plans.
  - Be extensible.

Defining tracking plans as code should not prohibit use of a SaaS Analytics Governance tool. These systems should work in unison.

Reflekt is making the following bets about product analytics and the teams doing this work:
- More explicit tracking. Less implicit tracking.
- More product analytics powered by the data warehouse and dbt.
- [dbt metrics](https://docs.getdbt.com/docs/building-a-dbt-project/metrics) and the [metrics layer](https://docs.getdbt.com/docs/dbt-cloud/using-dbt-cloud/cloud-metrics-layer) - imagine defining metrics *in the tracking plan* and having the dbt metric templated by Reflekt 🤯

## Reporting bugs
If you want to report a bug or request a feature, please open an [issue](https://github.com/GClunies/reflekt/issues).

## Contributing code
Please feel free to open a [Pull Request](https://github.com/GClunies/reflekt/pulls) for contributions you would like to propose. Please see the [contributing](docs/CONTRIBUTING-CODE.md) docs for development environment details and guidance.
