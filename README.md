<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# reflekt
reflekt is a command-line interface (CLI) and continuous integration (CI) tool for your tracking plan, defining it as `code`. reflekt uses these codified tracking plans to template dbt packages in which:
- The raw data source for every event is defined in your dbt sources.
- Every event has a dbt model.
- Every event is documented in your dbt docs.

**reflekt dbt DEMO GIF HERE**

reflekt integrates with your CDP and Analytics Governance tools to help bring DevOps best practices to how you create, iterate, and manage tracking plans and product analytics.

**reflekt pull DEMO GIF HERE**

See the sections below for a full list of integrations and commands.


## Tracking plans as `code`
reflekt tracking plan code is:
- **Human readable**. reflekt plans can be read and understood by technical *and* business users.
- **Version controlled**. Create tracking plan branches for dev, staging, and production. Submit PRs. Revert when things break.
- Able to support **Metadata**, customizable for unique use cases.
- **Testable**. Naming conventions, prohibited property names, expected metadata, etc. are all testable. You decide when to run tests to suit your continuos-integration strategy and tooling.
- **Extensible**. Enabling integration with other tools in the data stack (e.g. Segment, Avo, dbt, Amplitude, etc.). Build custom data pipelines and products using reflekt's artifacts.
- **Modular**. You choose what features to use. Prefer to manage your tracking plan in Segment/Avo/etc? No problem, you can still use reflekt to template your dbt packages.

Every reflekt project has a `reflekt_project.yml`, which sets project wide configurations.
<br>

<details><summary><code>reflekt_project.yml</code> (click to expand)</summary><p>

```yaml
# reflekt_project.yml

name: default_project

config_profile: default_profile  # Profile defined in reflekt_config.yml
# config_path: /absolute/path/to/reflekt_config.yml  # OPTIONAL - Absolute path to reflekt_config.yml

tracking-plans:
naming: # REQUIRED - For `events:` and `properties:` below
    #   - Provide one of `casing` or `pattern` (regex).
    #   - Set whether numbers are allowed in event/property names
    events:
    case: title  # One of title|snake|camel
    allow_numbers: true
    # pattern: '\b([a-z]*)([A-Z][a-z]+)+\b'
    reserved: []  # Reserved event names not allowed (casing matters)

    properties:
    case: snake  # One of title|snake|camel
    allow_numbers: true
    # pattern: '[A-Z][a-z]+'s
    reserved: [] # Reserved property names not allowed (casing matters)

data_types:  # REQUIRED - Specify allowed data types
    allowed:   # Available data types are listed below
    - string
    - integer
    - boolean
    - number
    - object
    - array
    - any

# OPTIONAL - Define a schema to ensure certain metadata is always defined for your events. This can be anything you want!
# Running `reflekt test --name <plan-name>` will check the metadata schema is upheld for all events
# To begin enforcing event metadata, uncomment the `metadata` block below and modify as needed
metadata:
    schema:
    product_owner:
        type: string
        required: true
    code_owner:
        required: true
        type: string
    priority:
    required: true
    type: integer
    allowed:
        - 1
        - 2
        - 3

dbt:
schema_map: # REQUIRED
    # For each tracking plan in your reflekt project, you must specify the schema in the data warehouse where raw event data is stored.
    my-plan: my_schema
sources:
    prefix: reflekt_src_  # REQUIRED - prefix for dbt package source files
models:
    prefix: reflekt_stg_  # REQUIRED - prefix for dbt package staging models & docs
    incremental_logic: |  # REQUIRED - Specify the incremental logic to use when templating dbt models. This should include the {%- if is_incremental() %} ... {%- endif %} block
    {%- if is_incremental() %}
    where received_at >= ( select max(received_at_tstamp) from {{ this }} )
    {%- endif %}
    # See this article for details on dbt incremental logic: https://discourse.getdbt.com/t/on-the-limits-of-incrementality/303
```
</p></details>

<br>

An example spec for a `Product Added` event.
<details><summary><code>product-added.yml</code> (click to expand)</summary><p>

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


## Install
1. Install `reflekt` with `pip`. Recommend installing in a virtual Python environment.
   ```bash
   pip install reflekt
   ```

2. Create a reflekt project.
   ```bash
   reflekt init --project-dir ./my_reflekt_project  # Follow the prompts
   cd my_reflekt_project                            # Navigate inside project
   ```

Your reflekt project includes an example tracking plan in the `tracking-plans/` folder.

## Commands
Create a new tracking plan in the reflekt spec
```zsh
$ reflekt new --name <plan-name>
```
<br>

Get a tracking plan from your CDP or Analytics Governance tool and convert it to YAML in reflekt spec
```zsh
$ reflekt pull --name <plan-name>
```
<br>

Sync a reflekt tracking plan to your CDP or Analytics Governance tool. reflekt handles the conversion!
```zsh
$ reflekt push --name <plan-name>
```
<br>

Test a reflekt tracking plan for naming conventions, allowed data types, and expected metadata across all your events. All tests are configured in your `reflect_project.yml`.
```zsh
$ reflekt test --name <plan-name>
```

Build a dbt package with sources, staging models, and documentation.
```zsh
$ reflekt dbt --name <plan-name>
```

## Integrations
### CDPs
- **Supported**: Segment
- **Under evaluation**: Rudderstack, Snowplow

### Analytics Governance
- **Supported**:
  - Segment Protocols
  - Avo (reflekt pull, reflekt dbt only)
- **Under evaluation**: Iteratively (reflekt pull, reflekt dbt only), Amplitude Govern (reflekt push only)

### Transform
**Supported**: dbt

### Cloud Warehouses
- **Supported**: Snowflake, Redshift
- **Under evaluation**: BigQuery

<br>

## Contributing
Contributions are welcome. Please feel free to raise issues and submit PRs.

#### dev environment
reflekt uses [poetry](https://python-poetry.org/) for packaging and dependency management. If you use poetry, this repo includes `poetry.lock` and `pyproject.toml` files to help spin up a dev environment. Simply navigate to the root of this repo on your machine and run.
```bash
poetry install
```

If you prefer to use another solution (e.g. pipenv, venv, conda) for packaging and dependency management, a `requirements-dev.txt` is included in this repo as well.
