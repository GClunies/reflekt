<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# reflekt
**reflekt is a continuous integration tool for your tracking plan.** It integrates with your Analytics Governance Tool, Customer Data Platform (CDP), data warehouse, and [dbt](https://www.getdbt.com/).

![reflekt-arch](/docs/reflekt-arch.png)

reflekt defines tracking plans as `code`. This code powers reflekt's **dbt package templater**, which parses the tracking plan code and writes a dbt package modeling your first-party data. Every reflekt dbt package includes:
- dbt [sources](https://docs.getdbt.com/docs/building-a-dbt-project/using-sources) pointing to the schema and tables in your warehouse where the raw event data is stored.
- dbt [models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) for every event in your tracking plan. Light transformations are applied to prepare the data for consumption or further modeling.
- dbt [documentation](https://docs.getdbt.com/docs/building-a-dbt-project/documentation) for every event in your tracking plan.

**reflekt pull & reflekt dbt DEMO GIF HERE**

**With reflekt, you can:**
- Stop writing models and documentation for each event manually. Template them using
  ```bash
  reflekt dbt --name my-plan  # Templates reflekt dbt package
  ```
- Test events in your tracking plan for naming conventions, required metadata, etc.
- Create new tracking plans.
- Get tracking plans from your Analytics Governance Tool.
- Sync tracking plan updates to your Analytics Governance Tool.
- Bump your reflekt dbt package version and re-template anytime your tracking plan changes.


See the sections below for a full list of [integrations](https://github.com/GClunies/reflekt#integrations) and [commands](https://github.com/GClunies/reflekt#integrations).

## Tracking plans as `code`
Every reflekt project has a `reflekt_project.yml`, which sets project wide configurations.
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

reflekt manages each tracking plan in a directory with corresponding YAML files for your events.

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

2. Create a reflekt project.
   ```bash
   $ reflekt init --project-dir ./my_reflekt_project  # Follow the prompts
   $ cd my_reflekt_project                            # Navigate inside project
   ```

Your reflekt project includes an example tracking plan in the `tracking-plans/` folder.

### Using reflekt with Avo
Pulling tracking plans from [Avo](https://www.avo.app/) requires additional setup and contacting Avo support:
1. Contact Avo support and request access to the JSON source.
2. Install node and npm. The [npm docs](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) provide great docs and guidance on this.
3. Install the [Avo CLI](https://www.avo.app/docs/implementation/cli) and verify installation.
   ```bash
   $ npm install -g avo
   $ avo --version
     2.0.2
   ```
4. Link your Avo Account and verify account.
   ```bash
   $ avo login
   $ avo whoami
     info Logged in as greg@reflekt-ci.com
   ```
5. Create a JSON source in Avo.
   1. Each of your applications (web, iOS, etc.) should have it's own JSON source.
   2. The JSON source name you set will be used by reflekt as the plan name when running `reflekt pull --name avo-json-source-name`.
   3. In the Avo source settings, under the **Avo Functions Setup** tab, be sure to set the **Programming Language** to `JSON Schema`.
6. Add events from your Avo plan to the Avo JSON source. The events should match the events collected on your application.
7. Configure Avo with Reflekt
   ```bash
   # From the root of your reflekt project
   $ cd .reflekt/avo

   $ avo init
     success Initialized for workspace patty-bar-dev
     info Run 'avo pull' to pull analytics wrappers from Avo

   $ avo pull --force
     info Pulling from branch 'main'
     info No sources configured.
     # You will be prompted for the following
     # Replace the values inside < > below with your own)
     ? Select a source to set up <select the JSON source you created>
     ? Select a folder to save the analytics wrapper in <select '.'>
     ? Select a filename for the analytics wrapper <your-avo-json-source-name.json>

     success Analytics wrapper successfully updated
     └─ your-avo-json-source-name
        └─ your-avo-json-source-name.json
   ```

  Going forward, you will only need to run `reflekt pull --name your-avo-json-source-name>` to get the latest version of your tracking plan from Avo.
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
### Customer Data Platforms (CDPs)
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

## Contributing
Feel free to raise issues and submit PRs.

#### dev environment
reflekt uses [poetry](https://python-poetry.org/) for packaging and dependency management. If you use poetry, this repo includes `poetry.lock` and `pyproject.toml` files to help spin up a dev environment. Simply navigate to the root of this repo on your machine and run.
```bash
poetry install
```

If you prefer to use another solution (e.g. pipenv, venv, conda) for packaging and dependency management, a `requirements-dev.txt` is included in this repo as well.
