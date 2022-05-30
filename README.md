<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt
Reflekt is a command line tool (CLI) allowing users to **automagically template dbt packages modeling and documenting all the events in tracking plans from their Analytics Governance tool,** which can be easily consumed by a dbt project. Each Reflekt dbt package includes:
- A dbt [source](https://docs.getdbt.com/docs/building-a-dbt-project/using-sources) pointing to the schema and tables in the warehouse where raw event data is loaded.
- A dbt [model](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) for each event in the tracking plan. Ready for consumption or further modeling.
- A dbt [doc](https://docs.getdbt.com/docs/building-a-dbt-project/documentation) entry for every model in the package, pulling information directly from the tracking plan. Your dbt docs *reflekt* your tracking plan. The data team and the business always know what your tables and columns mean.

Reflekt integrates with you Analytics Governance tool (e.g. [Segment Protocols](https://segment.com/docs/protocols/), [Avo](https://www.avo.app/)), Customer Data Platform (e.g. [Segment](https://segment.com/)), cloud data warehouse (e.g. [Snowflake](https://www.snowflake.com/)), and [dbt](https://www.getdbt.com/).

![reflekt-architecture](/docs/reflekt-arch-flow.jpg)

Reflekt's dbt package templater is powered by its ability to define tracking plans as `code`, making them an *extensible artifact*, similar to how many tools use dbt's `manifest.json` to power their functionality.

**!!! DEMO VIDEO GOES HERE !!!**

By defining tracking plans as code, they can be developed and managed using software engineer principles (version control, development branches, pull requests, reviews, and CI/CD). This is particularly useful for [Segment Protocols](https://segment.com/docs/protocols/) users who lack this functionality. With Reflekt, you can:
- Pull a tracking plan from your Analytics Governance tool, converting it to code.
- Push changes to tracking plan code back to your Analytics Governance Tool, Reflekt handles the conversion.
- Create a new tracking plan defined as code.
- Test tracking plan code for naming conventions and required metadata. All defined by rules in your `reflekt_project.yml`.

## Getting Started
- [Docs](docs/DOCUMENTATION.md/#reflekt-docs)
  - [Install](docs/DOCUMENTATION.md/#install)
  - [Setup](docs/DOCUMENTATION.md/#setup)
    - [Connecting Reflekt + Avo](docs/DOCUMENTATION.md/#connecting-reflekt--avo)
  - [Commands](docs/DOCUMENTATION.md/#commands)
  - [Reflekt project configuration](docs/DOCUMENTATION.md/#project-configuration)
  - [Tracking plans as `code`](docs/DOCUMENTATION.md/#tracking-plans-as-code)
- [Example Reflekt project](https://github.com/GClunies/patty-bar-reflekt) (used in demo above)

## Using Reflekt

**Reflekt exists to:**
- Save data teams time by templating dbt packages modeling all events in the tracking plan.
- Increase the use of software engineering workflows for tracking plan management.
- Allow teams to assess how tracking plan changes will affect downstream dbt models.

### Reflekt + Avo
[Avo](https://www.avo.app/) uses branches, environments, and naming conventions to manage tracking plans, bringing a workflow similar to software engineering into their web based UI.

**For Avo users, we recommend continuing to manage tracking plans in Avo, then connecting a Reflekt project to Avo** (see docs on [Connecting Reflekt + Avo](DOCUMENTATION.md/#connecting-reflekt--avo)). With this setup, you can:
- Pull the tracking plan from Avo as it changes (can specify Avo branch) into Reflekt.
  ```bash
  $ reflekt pull --name my-plan --avo-branch staging
  ```
  This creates a copy of the plan as code in the Reflekt project, to be used by Reflekt's dbt templater.

- Template a dbt package modeling and documenting all the events in the tracking plan. You can tell Reflekt to template based on data in specified schema (configure available schemas for plans in `reflekt_project.yml`).
  ```bash
  $ reflekt dbt --name my-plan --warehouse-schema my_app_staging
  ```

- Open a GitHub pull request with new/updated Reflekt dbt package. Get reviews from team members. Merge to main branch when approved.

- Reference Reflekt dbt packages in your dbt project.
  ```yaml
  # packages.yml in dbt project
  packages:
  - package: dbt-labs/dbt_utils
    version: 0.8.5

  - git: "https://github.com/my-github-user/reflekt-project-repo"
    subdirectory: "dbt_packages/reflekt_my_app_staging"
    revision: v0.1.0__reflekt_my_app_staging  # Git tag or full commit
  ```

In the example above, Reflekt know's about Avo's staging branch and the staging schema in the data warehouse, allowing you to assess how tracking plan changes will affect dependent dbt models ***before pushing tracking changes to production.***

### Reflekt + Segment Protocols
[Segment Protocols](https://segment.com/docs/protocols/) lets you manage tracking plans within your Segment account. While Segment does not use branches and environments, it does have an extensive API which Reflekt leverages.

**For Segment Protocols users, we recommend managing your tracking plans as `code` in a GitHub repository containing your Reflekt project.** With this setup, you can:
- Make changes to a tracking plan (e.g. add new event) by changing the tracking plan code.
  ```yaml
  # Adding a new event is easy!
  version: 1
  name: Example Event
  description: This is an example event.
  metadata:
    code_owner: me
  properties:
    name: example_property
    description: This is an example property.
    type: string
    required: true
  ```
- Template a dbt package modeling and documenting all the events in the tracking plan.
  ```bash
  $ reflekt dbt --name my-plan --warehouse-schema my_app
  ```
- Open pull requests in GitHub. Request reviews from team members, debate, and collaborate.
- Pull requests could trigger a CI suite in GitHub Actions that test tracking plans for naming conventions and expected metadata.
  <details><summary><strong>example-test-plans.yml</strong> (click to expand)</summary><p>

  ```yaml
  # test-plans.yml
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
  </p></details>

- On merge to main branch in GitHub, sync changes to Segment Protocols using a GitHub Action.
  <details><summary><strong>example-sync-plans.yml</strong> (click to expand)</summary><p>

  ```yaml
  # sync-plans.yml
  name: Sync Tracking Plans
  on: pull_request

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
  </p></details>

- Reference Reflekt dbt packages in your dbt project.
  ```yaml
  # packages.yml in dbt project
  packages:
  - package: dbt-labs/dbt_utils
    version: 0.8.5

  - git: "https://github.com/my-github-user/reflekt-project-repo"
    subdirectory: "dbt_packages/reflekt_my_app"
    revision: v0.1.0__reflekt_my_app  # Git tag or full commit
  ```

## Reporting bugs
If you want to report a bug or request a feature, please open an [issue](https://github.com/GClunies/reflekt/issues).

## Contributing code
Feel free to open a [Pull Request](https://github.com/GClunies/reflekt/pulls) for contributions you would like to propose.

#### Development environment
reflekt uses [poetry](https://python-poetry.org/) for packaging and dependency management. If you use poetry, this repo includes `poetry.lock` and `pyproject.toml` files to help spin up a dev environment.

If you prefer to use another solution (e.g. pipenv, venv, conda) for packaging and dependency management, a `requirements-dev.txt` is included in this repo as well.
