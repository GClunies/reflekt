<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt
**Reflekt is a continuous integration tool for your tracking plan.** It integrates with your Analytics Governance Tool, Customer Data Platform (CDP), data warehouse, and [dbt](https://www.getdbt.com/).

![reflekt-arch](/docs/reflekt_architecture.png)

Reflekt defines tracking plans as `code`. This code powers Reflekt's **dbt package templater**, which parses the tracking plan code and writes a **dbt package modeling all events in your tracking plan**, ready for use in your dbt project.

Every Reflekt dbt package includes:
- dbt [sources](https://docs.getdbt.com/docs/building-a-dbt-project/using-sources) pointing to the schema and tables in your warehouse where the raw event data is stored.
- dbt [models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) for every event in your tracking plan. Light transformations are applied to prepare data for consumption and further modeling.
- dbt [documentation](https://docs.getdbt.com/docs/building-a-dbt-project/documentation) for every event in your tracking plan. To be consumed by analysts and the business.

Your dbt models and documentation should *reflekt* the information you've already defined in your tracking plan.

## Commands
**With Reflekt, you can**

Stop manually writing dbt models and documentation for each event you track. Template them using. Bump your Reflekt dbt package version and re-template anytime your tracking plan changes.
```bash
$ reflekt dbt --name <plan-name>
```

Test events and properties in your tracking plan for naming conventions, data types, and expected metadata.
```zsh
$ reflekt test --name <plan-name>
```

Create a new tracking plan, defined as code.
```bash
$ reflekt new --name <plan-name>
```

Get tracking plans from your Analytics Governance Tool (Segment Protocols, Avo, others coming soon) and convert it to a Reflekt tracking plan, ready to be templated as a dbt package.
```bash
$ reflekt pull --name <plan-name>
```

Sync your Reflekt tracking plan to your Analytics Governance tool (Segment Protocols, others coming soon). Reflekt handles the conversion!
```bash
$ reflekt push --name <plan-name>
```

## Tracking plans as `code`
Every Reflekt project has a `reflekt_project.yml`, which sets project wide configurations.
<br>

<details><summary>Example <code>reflekt_project.yml</code> (click to expand)</summary><p>

```yaml
# reflekt_project.yml

# NOTE - Configs below are required unless flagged with # OPTIONAL comment

name: default_project

config_profile: default_profile  # Profile defined in reflekt_config.yml

# config_path: /absolute/path/to/reflekt_config.yml  # OPTIONAL

tracking_plans:
  naming:
    # For `events:` and `properties:` below:
    #   - Provide one of `casing` or `pattern` (regex).
    #   - Set whether numbers are allowed in event/property names
    events:
      case: title  # One of title|snake|camel
      # pattern: 'your-regex-here'
      allow_numbers: true
      reserved: []  # Reserved event names (casing matters)

    properties:
      case: snake  # One of title|snake|camel
      # pattern: 'your-regex-here'
      allow_numbers: true
      reserved: [] # Reserved property names (casing matters)

  data_types:
    # Specify allowed data types. Available types listed below
    allowed:
      - string
      - integer
      - boolean
      - number
      - object
      - array
      - any
      - 'null'  # Specify null type in quotes

  plan_db_schemas:
    # For each reflekt tracking plan, specify schema in database with raw event data.
    # Replace the example mapping below with your mappings
    example-plan: example_schema

  # OPTIONAL (uncomment `metadata:` block to use)
  # Define a schema for event metadata, this is tested when running
  #     `reflekt test --name <plan-name>`
  metadata:
    schema:
      # Example metadata schema
      product_owner: John
        type: string
        required: true
      code_owner: Jane
        required: true
        type: string
      stakeholders:
        type: string
        allowed:
          - Product
          - Engineering
          - Data

dbt:
  sources:
    # Prefix for dbt package sources
    prefix: src_reflekt_

  models:
    # Prefix for dbt package staging models & docs
    prefix: reflekt_
    materialized: incremental  # One of view|incremental
    # OPTIONAL (Required if `materialized: incremental`)
    # `incremental_logic:` specifies incremental logic to use when templating dbt models.
    # This should include the {%- if is_incremental() %} ... {%- endif %} block
    # Article on dbt incremental logic: https://discourse.getdbt.com/t/on-the-limits-of-incrementality/303
    incremental_logic: |
      {%- if is_incremental() %}
      where received_at >= ( select max(received_at_tstamp)::date from {{ this }} )
      {%- endif %}

  # OPTIONAL
  # For each reflekt tracking plan, you can specify the schema where dbt pkg
  # models will be materialized. Uncomment `pkg_db_schemas:` block to use.
  pkg_db_schemas:
    example-plan: example_schema

```
</p></details>
<br>

Reflekt manages each tracking plan in a directory with corresponding YAML files for your events.

![my-plan](/docs/my-plan.png)

<details><summary>Example <code>product-added.yml</code> (click to expand)</summary><p>

```yaml
# product-added.yml
- version: 1
  name: Product Added
  description: Fired when a user adds a product to their cart.
  metadata:  # Set event metadata. Configure metadata tests in reflekt_project.yml
    product_owner: pm-name
    code_owner: eng-squad-1
    priority: 1
  properties:
    - name: cart_id
      description: Cart ID to which the product was added to.
      type: string
      required: true    # Specify property is required
    - name: product_id
      description: Database ID of the product being viewed.
      type: integer
      required: true
    - name: name
      description: Name of the product.
      type: string     # Specify property type
      required: true
    - name: variant
      description: Variant of the product (e.g. small, medium, large).
      type: string
      enum:            # Enumerated list of allowed values
        - small
        - medium
        - large
      required: false  # Property is not required
    - name: price
      description: Price ($) of the product added to the cart.
      type: number
      required: true
    - name: quantity
      description: Quantity of the product added to the cart.
      type: integer
      required: true
```
</p></details>


## Install & Setup
1. Install `reflekt` with `pip`. Recommend installing in a virtual Python environment.
   ```bash
   $ pip install reflekt
   ```

2. Create a Reflekt project.
   ```bash
   $ reflekt init --project-dir ./my_reflekt_project  # Follow the prompts
   $ cd my_reflekt_project                            # Navigate inside project
   ```

Your Reflekt project includes an example tracking plan in the `tracking-plans/` folder.

#### reflekt with Avo
Using Reflekt with Avo is an experimental feature. It requires additional setup and configuration - see the docs on [using reflekt with Avo](docs/reflekt-with-avo.md).

## Integrations
### Customer Data Platforms (CDPs)
- **Supported**:
  - Segment
- **Researching**:
  - Rudderstack
  - Snowplow

### Analytics Governance Tools
- **Supported**:
  - Segment Protocols
  - Avo (*experimental* - only supports `reflekt pull` and `reflekt dbt`)
- **Researching**:
  - Rudderstack Data Governance API
  - Snowplow Data Structures API
  - Iteratively (reflekt pull, reflekt dbt only)

### Transform
**Supported**: dbt

### Cloud Warehouses
- **Supported**: Snowflake, Redshift
- **Researching**: BigQuery

## Contributing
Feel free to raise issues and submit PRs.

#### dev environment
reflekt uses [poetry](https://python-poetry.org/) for packaging and dependency management. If you use poetry, this repo includes `poetry.lock` and `pyproject.toml` files to help spin up a dev environment. Simply navigate to the root of this repo on your machine and run.
```bash
poetry install
```

If you prefer to use another solution (e.g. pipenv, venv, conda) for packaging and dependency management, a `requirements-dev.txt` is included in this repo as well.
