<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt
**Reflekt is a command line interface and continuous integration tool for your tracking plan.** It integrates with your Analytics Governance Tool, Customer Data Platform (CDP), data warehouse, and [dbt](https://www.getdbt.com/).

![reflekt-arch](/docs/reflekt_architecture.png)

Reflekt defines tracking plans as `code`, powering its **dbt package templater** to write dbt packages modeling **all the events in your tracking plan**. Every Reflekt dbt package includes:
- dbt [sources](https://docs.getdbt.com/docs/building-a-dbt-project/using-sources) pointing to the schema and tables in your warehouse where the raw event data is stored.
- dbt [models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) for every event in your tracking plan. These models include light transformations to make your event data ready for consumption or further modeling.
- dbt [documentation](https://docs.getdbt.com/docs/building-a-dbt-project/documentation) for every model in the package based on the information in the tracking plan. Analysts and the business always know what your tables and columns mean.

https://user-images.githubusercontent.com/28986302/169673197-f5ae1d60-682d-4c85-ad82-4f7fb31be128.mp4

## Getting started
- [Install & Setup](docs/INSTALL-SETUP.md)
- [Tracking plan as code](docs/TRACKING-PLANS-AS-CODE.md)
- [Commands](docs/COMMANDS.md)
- [Integrations](docs/INTEGRATIONS.md) (Analytics Governance Tools, CDPs, warehouses)

### Motivations
I built Reflekt to:
- Automate writing dbt sources, models, and documentation for event data. We know we *should* do this, but doing it for all events (sometimes 100s) can be daunting, time consuming, and boring.
- Never manage a tracking plan in a spreadsheet again.
- Improve the utility of [Segment Protocols](https://segment.com/docs/protocols/) and the value it provides.
  - [Avo](https://www.avo.app/) is a refreshing step forward relative to Segment Protocols, so integration for future projects was desired.

### Beliefs
**The tracking plan is the most important artifact in a product analytics stack.** Without one, product and data team can easily find themselves lost. The tracking code a developer writes, how events are validated, raw data in the warehouse, transformed data, documentation, insights from analysts - are all dependent on the tracking plan. Tracking plans should be:
- Able to be represented as `code`. This code *does not* prohibit the use of a SaaS Analytics Governance tools (e.g. Avo). These systems should work in unison.
- Version controlled, with branches and environments for different development stages (i.e. dev/staging/prod).
- Extensible (e.g. Reflekt's dbt templater), powering integrations with other tools in the stack.
- Support user-defined metadata (e.g. a "code owner" for each event).
- Leverage continuous integration to test and deploy plans, events, and properties.

### Bets
Reflekt bets on the following trends concerning modern product analytics:
- More explicit tracking. Less implicit tracking.
- Product analytics increasingly powered by the data warehouse and dbt.
- [dbt metrics](https://docs.getdbt.com/docs/building-a-dbt-project/metrics) and the [metrics layer](https://docs.getdbt.com/docs/dbt-cloud/using-dbt-cloud/cloud-metrics-layer) - Imagine defining metrics *in the tracking plan* and Reflekt templating them in dbt for you. 📈

## Reporting bugs
If you want to report a bug or request a feature, please open an [issue](https://github.com/GClunies/reflekt/issues).

## Contributing code
Feel free to open a [Pull Request](https://github.com/GClunies/reflekt/pulls) for contributions you would like to propose. See the [contributing](docs/CONTRIBUTING-CODE.md) docs for development environment details and guidance.
