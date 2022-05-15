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

## Commands
1. Create a Reflekt project.
   ```bash
   $ reflekt init --project-dir ./my_reflekt_project  # Follow the prompts
   ```

2. Get a tracking plan from your Analytics Governance Tool (Segment Protocols, Avo, others coming soon) and convert it to a Reflekt tracking plan code, ready for templating.
   ```bash
   $ reflekt pull --name <plan-name>
   ```

3. Use the Reflekt dbt templater to save your data team time. Stop manually writing dbt source, models, and documentation for your event data.
   ```bash
   $ reflekt dbt --name <plan-name>
   ```
   As your tracking plan changes, re-template to capture updates/changes. Reflekt will bump the version of your dbt package as it evolves with your tracking plan.

4. Sync your Reflekt tracking plan to your Analytics Governance tool (Segment Protocols, others coming soon). Reflekt handles the conversion!
   ```bash
   $ reflekt push --name <plan-name>
   ```

5. Test events and properties in your tracking plan for naming conventions, data types, and expected metadata.
   ```zsh
   $ reflekt test --name <plan-name>
   ```

6. Create a new tracking plan, defined as code.
   ```bash
   $ reflekt new --name <plan-name>
   ```

## Tracking plans as `code`
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
<br>

Every Reflekt project has a `reflekt_project.yml`, which sets project wide configurations.
<br>

<details><summary>Example <code>reflekt_project.yml</code> (click to expand)</summary><p>

```yaml
# reflekt_project.yml

# Configurations are REQUIRED unless flagged by an '# OPTIONAL (optional_config:)' comment
# Uncomment OPTIONAL configurations to use them

name: default_project

config_profile: default_profile  # Profile defined in reflekt_config.yml

# OPTIONAL (config_path:)
# config_path: /absolute/path/to/reflekt_config.yml

tracking_plans:
  naming:  # Naming conventions for tracking plans
    events:
      case: title  # One of title|snake|camel
      allow_numbers: true
      reserved: []  # Reserved event names (casing matters)

    properties:
      case: snake  # One of title|snake|camel
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
    # For each reflekt tracking plan, specify the schema in your data warehouse storing raw data.
    # Replace the example mapping below with your mappings
    example-plan: example_schema

  # OPTIONAL (metadata:)
  # Define a validation schema for your metadata. This is tested when running
  #     reflekt test --name <plan-name>
  # Uses Cerberus validation rules (https://bit.ly/3vIsAfs) to define schemas.
  metadata:
    schema:
      # Example metadata schema
      product_owner:
        type: string
        required: true
      code_owner:
        required: true
        type: string
      stakeholders:
        type: string
        required: false
        allowed:
          - Product
          - Engineering
          - Data

dbt_templater:
  sources:
    prefix: src_reflekt_       # Prefix for templated dbt package sources

  models:
    prefix: reflekt_           # Prefix for models & docs in templated dbt package
    materialized: incremental  # One of view|incremental
    # OPTIONAL (incremental_logic:) [REQUIRED if 'materialized: incremental']
    # Specify the incremental logic to use when templating dbt models.
    # Must include the {%- if is_incremental() %} ... {%- endif %} block
    incremental_logic: |
      {%- if is_incremental() %}
      where received_at >= ( select max(received_at_tstamp)::date from {{ this }} )
      {%- endif %}

  # OPTIONAL (pkg_db_schemas:)
  # For each reflekt tracking plan, you can override the schema where the
  # models in the templated dbt package will be created.
  pkg_db_schemas:
    example-plan: example_schema

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
