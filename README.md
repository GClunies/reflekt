<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# reflekt
reflekt is a command-line interface (CLI) and continuous integration (CI) tool for your tracking plan, defining it as `code`. reflekt uses this codified tracking plan to template a dbt package in which:
- Every event has a dbt source, pointing to the raw data in your warehouse.
- Every event has a dbt model.
- Every event is documented in your dbt docs.

**reflekt dbt DEMO GIF HERE**

reflekt integrates with your CDP and Analytics Governance tools to help bring DevOps best practices to how you create, iterate, and manage tracking plans and product analytics.

**reflekt pull DEMO GIF HERE**

See the sections below for a full list of [integrations](https://github.com/GClunies/reflekt#integrations) and [commands](https://github.com/GClunies/reflekt#integrations).


## Tracking plans as `code`
reflekt tracking plan code is:
- **Human readable**. No JSON schema here. Using YAML improves readability for technical *and* business users.
- **Version controlled**. Create branches for dev, staging, and production plans. Submit PRs. Review with your team. Revert when things break.
- Able to support **Metadata**, customizable for your unique use cases.
- **Testable**. Naming conventions, prohibited property names, expected metadata, etc. are all testable. You decide when to run tests to suit your CI strategy and tooling.
- **Extensible**. reflekt integrates with your product analytics tools and data stack (e.g. Segment, Avo, dbt, Amplitude, etc.). Build custom data pipelines and products using reflekt's artifacts.
- **Modular**. You choose what features to use. Prefer to manage your tracking plan in Segment/Avo/etc? No problem, you can still use reflekt to template your dbt packages.

Every reflekt project has a `reflekt_project.yml`, which sets project wide configurations.
<br>

<details><summary><code>reflekt_project.yml</code> (click to expand)</summary><p>

```yaml
# reflekt_project.yml

# NOTE - All configurations in this reflekt_project.yml are REQUIRED unless flagged with an # OPTIONAL comment

name: project_name  # Defined during `reflekt init`

config_profile: profile_name  # Defined during `reflekt init`. Must match a profile found in reflekt_config.yml

tracking_plans:
  naming:
    # For `events:` and `properties:` below:
    #   - Provide one of `casing` or `pattern` (regex). Not both.
    #   - Set whether numbers are allowed in event/property names
    events:
      case: title  # One of title|snake|camel
      # pattern: 'your-regex-here'
      allow_numbers: false
      reserved: []  # Reserved event names (casing matters)

    properties:
      case: camel
      # pattern: 'your-regex-here'
      allow_numbers: false
      reserved: []  # Reserved property names (casing matters)

  data_types:
    # Specify allowed data types. Available types listed below
    allowed:
      - string
      - integer
      - boolean
      - number
      - object
      - array

  plan_db_schemas:
    # For each reflekt tracking plan, specify schema in database with raw event data.
    # Replace the example mapping below with your mappings
    your-plan-name: schema_with_raw_data

  metadata:  # OPTIONAL
    # Define a schema for event metadata, this is tested when running
    #     `reflekt test --name <plan-name>`
    schema:
      code_owner:
        required: true
        type: string
        allowed:
          - John
          - Jane
      product_owner:
        required: true
        type: string
        allowed:
          - Jim
          - Jen
      priority:
        required: true
        type: integer
        allowed:
          - 1
          - 2

dbt:
  sources:
    # Prefix for dbt package source files
    prefix: src_reflekt_

  models:
    # Prefix for dbt package models & docs
    prefix: reflekt_
    # Specify incremental logic to use when templating dbt models.
    # This should include the {%- if is_incremental() %} ... {%- endif %} block
    # Article on dbt incremental logic: https://discourse.getdbt.com/t/on-the-limits-of-incrementality/303
    incremental_logic: |
      {%- if is_incremental() %}
      where received_at >= ( select max(received_at_tstamp)::date from {{ this }} )
      {%- endif %}

  pkg_db_schemas:  # OPTIONAL
    # For each reflekt tracking plan, you may specify a schema in database to materialize dbt pkg models.
    your-plan-name: analytics  # Or any other schema you want

```
</p></details>

<br>

reflekt manages each tracking plan in a directory with corresponding YAML files for your events.

**SCREEN SHOT GOES HERE OF PLAN FOLDER STRUCTURE**

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

Build a dbt package with sources, models, and documentation.
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
