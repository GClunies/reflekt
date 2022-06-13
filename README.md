<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt
Reflekt lets data teams:
- **Define tracking plans as `code`, encouraging tracking design using software engineering principles** (version control, branches, pull requests, reviews, and CI/CD).
- **Automagically build a dbt package that models and documents the events in a tracking plan** pulled from an Analytics Governance tool, ready for use in a dbt project.

Each Reflekt dbt package includes:
- A dbt [source](https://docs.getdbt.com/docs/building-a-dbt-project/using-sources) pointing to the schema and tables in the warehouse where the raw event data is loaded.
- A dbt [model](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) for each event in the tracking plan. Ready for consumption or use in downstream models.
- A dbt [doc](https://docs.getdbt.com/docs/building-a-dbt-project/documentation) entry for every event modeled in the package. These docs are a perfect *reflektion* of the tracking plan, ensuring the data team and business always know what a model and its columns mean.

https://user-images.githubusercontent.com/28986302/171330405-57400ead-574d-4b71-a31b-57935e0ba9e8.mp4

## Getting Started
Install Reflekt with `pip`.
```bash
pip install reflekt
```

  - [How it works](#how-it-works)
  - [Reflekt Documentation](docs/DOCUMENTATION.md/#reflekt-docs)
    - [Create a Reflekt project](docs/DOCUMENTATION.md/#create-a-reflekt-project)
    - [Project configuration](docs/DOCUMENTATION.md/#project-configuration)
    - [Tracking plans as `code`](docs/DOCUMENTATION.md/#tracking-plans-as-code)
    - [Commands](docs/DOCUMENTATION.md/#commands)
  - [Usage](#usage)
    - [Using Reflekt + Avo](#using-reflekt--avo)
    - [Using Reflekt + Segment Protocols](#using-reflekt--segment-protocols)
  - [Supported Integrations](#supported-integrations)
  - [Reporting bugs](#reporting-bugs)
  - [Contributing code](#contributing-code)


## How it works
Reflekt connects with your Analytics Governance tool (e.g. Avo, Segment Protocols), Customer Data Platform (e.g. Segment), Data Warehouse, and dbt.

![reflekt-architecture](/docs/reflekt-arch-flow.jpg)

## Usage
Reflekt is *modular*, which means that you can use *all* of Reflekt's features, or *only the features you need*. Recommended workflows to use Reflekt with various Analytics Governance tools are outlined below (after the demo video).

https://user-images.githubusercontent.com/28986302/171340104-f4a6f989-4c6b-4ca9-985c-c482c7e234e0.mp4

### Using Reflekt + Avo
For [Avo](https://www.avo.app/) users, **we recommended to continue to manage your tracking plan in Avo**, then use Reflekt to template dbt packages of your event data to be use in dbt. With this setup, you can:
- Run `reflekt pull --name my-plan` to pull a tracking plan from Avo into your local Reflekt project. This creates a codified version of your plan.
- Run `reflekt dbt --name my-plan --schema my_app_web_prod` to template a Reflekt dbt package that models and documents the events in your tracking plan.
- Push your changes to the GitHub repo where your Reflekt project is saved.
- Open a pull request to merge your templated Reflekt dbt package (e.g. `reflekt_my_app_web`) to your main branch. Request a review from team. Merge to the main branch when approved.
- In your dbt project, reference the Reflekt dbt package.
  ```yaml
  # packages.yml in dbt project
  packages:
  - package: dbt-labs/dbt_utils
    version: 0.8.5

  - git: "https://github.com/my-github-user/reflekt-project-repo"
    subdirectory: "dbt_packages/reflekt_my_app_web"
    revision: v0.1.0__reflekt_my_app_web  # Git tag created by 'reflekt dbt'
  ```
- Use the models from your Reflekt dbt package in your dbt project!
  ```sql
  -- daily_orders.sql
  {{
    config(
      materialized = 'view',
    )
  }}

  with

  reflekt_pkg_model as (

      select * from {{ ref('reflekt_my_app_web__order_completed') }}

  ),

  final as (

      select
          tstamp::date as date_day,
          count(*) as count_orders

      from reflekt_pkg_model
      group by 1

  )

  select * from final
  ```

### Using Reflekt + Segment Protocols
[Segment Protocols](https://segment.com/docs/protocols/) lets you manage tracking plans within your Segment account. While Segment Protocols does not use branches or environments, it does have a robust API. Reflekt leverages this API to enable managing tracking plans using software engineering principles** (version control, branches, pull requests, reviews, and CI/CD)

For Segment Protocols users, **we recommended to manage tracking plans as `code` in a GitHub repository containing your Reflekt project**. With this setup, you can:

- Make changes to a tracking plan by changing the tracking plan code.
  ```yaml
  version: 1
  name: Example Event
  description: This is an example event.
  metadata:
    code_owner: me
  properties:
    name: existing_property
    description: A property already tracked on product.
    type: integer
    required: true
    name: new_property
    description: A new property I am adding to be tracked.
    type: string
    required: false
  ```

- Push your tracking plan changes to the GitHub repo where your Reflekt project is saved.

- Open a Pull Request (PR) in GitHub to merge plan changes. Request a review from team. The PR could trigger a CI suite in GitHub Actions to test your changes follow your naming conventions and metadata expectations.
  ```yaml
  # .github/workflows/test-plans.yml
  name: Test Tracking Plans
  on: pull_request

  jobs:
    test:
      name: Test Tracking Plans
      strategy:
        fail-fast: false
        matrix:
          os: ['ubuntu-latest']
          python-version: ['3.9']
      runs-on: ${{ matrix.os }}
      steps:
        - name: Checkout Repo
          uses: actions/checkout@v2
        - name: Install Python ${{ matrix.python-version }}
          uses: actions/setup-python@v3
          with:
            python: ${{ matrix.python-version }}
        - name: Install Reflekt
          run: |
            pip install reflekt
        - name: Run reflekt test
          run: |
            reflekt test --name my-plan
  ```

- Merge to the main branch when approved, triggering a GitHub Action to sync your changes to Segment Protocols using `reflekt push --name my-plan`.
  ```yaml
  # .github/workflows/sync-plans.yml
  name: Sync Tracking Plans
  on:
    push:
      branches:
        - main

  jobs:
    test:
      name: Sync Tracking Plans
      strategy:
        fail-fast: false
        matrix:
          os: ['ubuntu-latest']
          python-version: ['3.9']
      runs-on: ${{ matrix.os }}
      steps:
        - name: Checkout Repo
          uses: actions/checkout@v2
        - name: Install Python ${{ matrix.python-version }}
          uses: actions/setup-python@v3
          with:
            python: ${{ matrix.python-version }}
        - name: Install Reflekt
          run: |
            pip install reflekt
        - name: Run reflekt test
          run: |
            reflekt push --name my-plan
  ```

You can now follow a similar process as outlined for Avo above, shown again below for clarity.

- Run `reflekt dbt --name my-plan --schema my_app_web_prod` to template a Reflekt dbt package that models and documents the events in your tracking plan.

- Push your changes to the GitHub repo where your Reflekt project is saved.

- Open a pull request to merge your templated Reflekt dbt package (e.g. `reflekt_my_app_web`) to your main branch. Request a review from team. Merge to the main branch when approved.
- In your dbt project, reference the Reflekt dbt package.
  ```yaml
  # packages.yml in dbt project
  packages:
  - package: dbt-labs/dbt_utils
    version: 0.8.5

  - git: "https://github.com/my-github-user/reflekt-project-repo"
    subdirectory: "dbt_packages/reflekt_my_app_web"
    revision: v0.1.0__reflekt_my_app_web  # Git tag created by 'reflekt dbt'
  ```

- Use the models from your Reflekt dbt package in your dbt project!
  ```sql
  -- daily_orders.sql
  {{
    config(
      materialized = 'view',
    )
  }}

  with

  reflekt_pkg_model as (

      select * from {{ ref('reflekt_my_app_web__order_completed') }}

  ),

  final as (

      select
          tstamp::date as date_day,
          count(*) as count_orders

      from reflekt_pkg_model
      group by 1

  )

  select * from final
  ```

## Supported integrations

| Integration Type     | Supported              | Developing | Considering                                   |
|----------------------|------------------------|------------|-----------------------------------------------|
| CDP                  | [Segment](https://segment.com/)                |            | [Rudderstack](https://www.rudderstack.com/), [Snowplow](https://snowplowanalytics.com/snowplow-bdp/)                         |
| Analytics Governance | [Avo](https://www.avo.app/), [Segment Protocols](https://segment.com/docs/protocols/) |            | [RudderStack Data Governance API](https://www.rudderstack.com/docs/data-governance/rudderstack-data-governance-api/), [Snowplow BDP Data Structures](https://docs.snowplowanalytics.com/docs/understanding-tracking-design/managing-data-structures-via-the-api-2/) |
| Warehouse            | [Snowflake](https://www.snowflake.com/), [Redshift](https://aws.amazon.com/redshift/)    |            | [BigQuery](https://cloud.google.com/bigquery)                                      |
| Transformation       | [dbt](https://www.getdbt.com/)                    | -          | -                                             |

## Reporting bugs
If you want to report a bug or request a feature, please open an [issue](https://github.com/GClunies/reflekt/issues).

## Contributing code
Contributions are welcome. Feel free to open a [Pull Request](https://github.com/GClunies/reflekt/pulls).

#### Development environment
reflekt uses [poetry](https://python-poetry.org/) for packaging and dependency management. If you use poetry, this repo includes `poetry.lock` and `pyproject.toml` files to help spin up a dev environment.

If you prefer to use another solution (e.g. pipenv, venv, conda) for packaging and dependency management, a `requirements-dev.txt` is included in this repo as well.
