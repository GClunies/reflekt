<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt
![PyPI](https://img.shields.io/pypi/v/reflekt?style=for-the-badge)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/reflekt?style=for-the-badge)
![GitHub](https://img.shields.io/github/license/gclunies/reflekt?style=for-the-badge)

> ***Product analytics is a team sport***

Reflekt helps Data, Engineering, and Product teams work together to define, manage, and model events for product analytics. Reflekt integrates with [schema registries](#interacting-with-schema-registries), cloud [data warehouses]((#supported-data-warehouses)), and [dbt](#dbt-artifacts).

- Define event schemas (aka data contracts) as `code` using [jsonschema](https://json-schema.org/). Schemas are version controlled, and stored in a GitHub repo.
- Configure naming and metadata conventions for events and properties. Lint schemas to test for compliance.
- Open pull requests (PRs) to propose schema changes, get input, and request reviews.
- Easily build a CI suite to [lint](#linting-schemas) schemas, [push](#push-schemas-to-a-registry) them to a schema registry, and [build corresponding dbt artifacts](#building-private-dbt-packages).

https://user-images.githubusercontent.com/28986302/217134526-df83ec90-86f3-491e-9588-b7cd56956db1.mp4

## Table of Contents
- [Getting Started](#usage)<br>
  - [Installation](#installation)<br>
  - [Reflekt `--help`](#reflekt-help)<br>
  - [Creating a project](#creating-a-project)<br>
  - [Project configuration](#project-configuration)<br>
- [Using Reflekt](#using-schemas)<br>
  - [Defining schemas](#defining-schemas)<br>
  - [Identifying and selecting schemas](#identifying-and-selecting-schemas)<br>
  - [Schema versions](#schema-versions)<br>
  - [Linting schemas](#linting-schemas)<br>
  - [Interacting with schema registries](#interacting-with-schema-registries)<br>
  - [Building dbt artifacts](#dbt-artifacts)<br>
  - [Supported data warehouses](#supported-data-warehouses)<br>

## Getting Started

### Installation
Reflekt is available on [PyPI](https://pypi.org/project/my-reflekt-project/). Install with `pip` (or package manager of choice), preferably in a virtual environment:
```bash
❯ source /path/to/venv/bin/activate  # Activate virtual environment
❯ pip install reflekt                # Install Reflekt
❯ reflekt --version                  # Confirm installation
Reflekt CLI Version: 0.3.1
```

### Reflekt `--help`
The `--help` flag provides an overview of available `reflekt` commands.
```bash
❯ reflekt --help  # Show general --help details

 Usage: reflekt [OPTIONS] COMMAND [ARGS]...

 Reflekt CLI.

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --version                                                                                                                                                        │
│ --install-completion        [bash|zsh|fish|powershell|pwsh]  Install completion for the specified shell. [default: None]                                         │
│ --show-completion           [bash|zsh|fish|powershell|pwsh]  Show completion for the specified shell, to copy it or customize the installation. [default: None]  │
│ --help                                                       Show this message and exit.                                                                         │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ build             Build data artifacts based on schemas.                                                                                                         │
│ debug             Check Reflekt project configuration.                                                                                                           │
│ init              Initialize a Reflekt project.                                                                                                                  │
│ lint              Lint schema(s) to test for naming and metadata conventions.                                                                                    │
│ pull              Pull schema(s) from a schema registry.                                                                                                         │
│ push              Push schema(s) to a schema registry.                                                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Each command also has a `--help` flag providing command details (arguments, options, syntax, etc.).
```bash
❯ reflekt lint --help  # Show --help details for `reflekt lint`

 Usage: reflekt lint [OPTIONS]

 Lint schema(s) to test for naming and metadata conventions.

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --select  -s      TEXT  Schema(s) to lint. [default: None] [required]                                                                                         │
│    --help                  Show this message and exit.                                                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### Creating a project
Create a new directory, initialize a new Git repo, and run `reflekt init` to create a new Reflekt project.
```bash
❯ mkdir ~/Repos/my-reflekt-project  # Create a new directory for the project
❯ cd ~/Repos/my-reflekt-project     # Navigate to the project directory
❯ git init                          # Initialize a new Git repo
❯ reflekt init                      # Initialize a new Reflekt project in the current directory

# Follow the prompts to configure the project
```

This will create a new Reflekt project with the following structure:
```bash
my-reflekt-project
├── .logs/                # Reflekt command logs
├── .reflekt_cache/       # Local cache used by Reflekt
├── artifacts/            # Where Reflekt builds data artifacts (i.e., dbt packages)
├── schemas/              # Where event schemas are defined and stored
├── .gitignore
├── README.md
└── reflekt_project.yml   # Project configuration
```

### Project configuration
Reflekt uses 3 files to configure a project: `reflekt_project.yml`, `reflekt_profiles.yml`, and `schemas/.reflekt/meta/1-0.json`. Under the hood, Reflekt validates these configuration files before running, raising errors if an invalid configuration is detected. Examples of each file with configuration details are found below.

#### **reflekt_project.yml**
Contains general project settings as well as configuration for schema conventions, schema registry details (if needed), and data artifact generation. Click to expand the example below with details on each setting.

<details>
<summary><code>example_reflekt_project.yml</code>(CLICK TO EXPAND)</summary>
<br>

```yaml
# Example reflekt_project.yml
# GENERAL CONFIG ----------------------------------------------------------------------
version: 1.0

name: reflekt_demo              # Project name
vendor: com.company_name        # Default vendor for schemas in reflekt project
default_profile: dev_reflekt    # Default profile to use from reflekt_profiles.yml
profiles_path: ~/.reflekt/reflekt_profiles.yml  # Path to reflekt_profiles.yml

# SCHEMAS CONFIG ----------------------------------------------------------------------
schemas:                        # Define schema conventions
  conventions:
    event:
      casing: title             # title | snake | camel | pascal | any
      numbers: false            # Allow numbers in event names
      reserved: []              # Reserved event names
    property:
      casing: snake             # title | snake | camel | pascal | any
      numbers: false            # Allow numbers in property names
      reserved: []              # Reserved property names
    data_types: [               # Allowed data types
        string, integer, number, boolean, object, array, any, 'null'
    ]

# REGISTRY CONFIG ---------------------------------------------------------------------
registry:                       # Additional config for schema registry if needed
  avo:                          # Avo specific config
    branches:                   # Provide ID for Avo branches for `reflekt pull` to work
      staging: AbC12dEfG        # Safe to version control (See Avo docs to find branch ID: https://bit.ly/avo-docs-branch-id)
      main: main                # 'main' always refers to the main branch

# ARTIFACTS CONFIG -----------------------------------------------------------------------
artifacts:                      # Configure how data artifacts are built
  dbt:                          # dbt package config
    sources:
      prefix: __src_            # Source files will start with this prefix
    models:
      prefix: stg_              # Model files will start with this prefix
    docs:
      prefix: _stg_             # Docs files will start with this prefix
      in_folder: false          # Docs files in separate folder?
      tests:                    # dbt tests to add based on column name (can be empty dict {})
        id: [unique, not_null]

```
</details>
<br>

#### **reflekt_profiles.yml**
Contains connection details for schema registries (used to validate event data) and data sources (i.e., data warehouse with raw event data). Click to expand the example below with details on each setting.
<details>
<summary><code>example_reflekt_profiles.yml</code>(CLICK TO EXPAND)</summary>
<br>

```yaml
# Example reflekt_profiles.yml
version: 1.0

dev_reflekt:                                              # Profile name (multiple profiles can be defined)
  # Define connections to schema registries (multiple allowed)
  registry:
    - type: segment
      api_token: segment_api_token                        # https://docs.segmentapis.com/tag/Getting-Started#section/Get-an-API-token
    - type: avo
      workspace_id: avo_workspace_id                      # https://www.avo.app/docs/public-api/export-tracking-plan#endpoint
      service_account_name: avo_service_account_name      # https://www.avo.app/docs/public-api/authentication#creating-service-accounts
      service_account_secret: avo_service_account_secret

  # Connections to data sources (data warehouses) where event data is stored.
  # Sources are uniquely identified by their ID and are used in the `--source` arg when running `reflekt build`.
  source:
    - id: snowflake             # For simplicity, we use the same ID as the source type.
      type: snowflake           # Snowflake DWH. Credentials follow.
      account: abc12345
      database: raw
      warehouse: transforming
      role: transformer
      user: reflekt_user
      password: reflekt_user_password

    - id: redshift              # For simplicity, we use the same ID as the source type.
      type: redshift            # Redshift DWH. Credentials follow.
      host: example-redshift-cluster-1.abc123.us-west-1.redshift.amazonaws.com
      database: analytics
      port: 5439
      user: reflekt_user
      password: reflekt_user_password

```
</details>
<br>

#### **schemas/.reflekt/meta/1-0.json**
A meta-schema used to validate all event schemas in the project. Under the hood, Reflekt uses this meta-schema along with the naming conventions defined in the `reflekt_project.yml` file to validate all event schemas.

To define ***required metadata*** for all event schemas in your project, you can update the `metadata` object in `schemas/.reflekt/meta/1-0.json`. See the example below showing how to require both **code owner** and **product owner** metadata.

<details>
<summary><code>schemas/.reflekt/meta/1-0.json</code>(CLICK TO EXPAND)</summary>
<br>

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": ".reflekt/meta/1-0.json",
    "description": "Meta-schema for all Reflekt events",
    "self": {
        "vendor": "reflekt",
        "name": "meta",
        "format": "jsonschema",
        "version": "1-0"
    },
    "type": "object",
    "allOf": [
        {
            "$ref": "http://json-schema.org/draft-07/schema#"
        },
        {
            "properties": {
                "self": {
                    "type": "object",
                    "properties": {
                        "vendor": {
                            "type": "string",
                            "description": "The company, application, team, or system that authored the schema (e.g., com.company, com.company.android, com.company.marketing)"
                        },
                        "name": {
                            "type": "string",
                            "description": "The schema name. Describes what the schema is meant to capture (e.g., pageViewed, clickedLink)"
                        },
                        "format": {
                            "type": "string",
                            "description": "The format of the schema",
                            "const": "jsonschema"
                        },
                        "version": {
                            "type": "string",
                            "description": "The schema version, in MODEL-ADDITION format (e.g., 1-0, 1-1, 2-3, etc.)",
                            "pattern": "^[1-9][0-9]*-(0|[1-9][0-9]*)$"
                        },
                        "metadata": {  // EXAMPLE: Defining required metadata (code_owner, product_owner)
                            "type": "object",
                            "description": "Required metadata for all event schemas",
                            "properties": {
                                "code_owner": {"type": "string"},
                                "product_owner": {"type": "string"}
                            },
                            "required": ["code_owner", "product_owner"],
                            "additionalProperties": false
                        },
                    },
                    "required": ["vendor", "name", "format", "version"],
                    "additionalProperties": false
                },
                "properties": {},
                "tests": {},
            },
            "required": ["self", "metadata", "properties"]
        }
    ]
}

```

</details>

<br>
<br>

## Using Reflekt
### Defining schemas
Event schemas are defined using [jsonschema](https://json-schema.org/). Each schema is defined as a separate JSON file, stored in the `schemas/` directory of a Reflekt project. An example `ProductClicked` event schema is shown below.

<details>
<summary><code>my-reflekt-project/schemas/segment/ecommerce/ProductClicked/1-0.json</code>(CLICK TO EXPAND)</summary>
<br>

```json
{
  "$id": "segment/ecommerce/ProductClicked/1-0.json",    // Unique ID for the schema
  "$schema": "http://json-schema.org/draft-07/schema#",  // JSON Schema version
  "self": {
      "vendor": "com.company_name",  // Company, application, team, or system that authored the schema
      "name": "ProductClicked",      // Name of the event
      "format": "jsonschema",        // Format of the schema
      "version": "1-0",              // Version of the schema
      "metadata": {                  // Metadata for the event
          "code_owner": "engineering/ecommerce-squad",
          "product_owner": "product_manager_name@company_name.com",
      }
  },
  "type": "object",
  "properties": {                   // Properties of the event
      "product_id": {
          "type": "string",
          "description": "Database id of the product being viewed"
      },
      "sku": {
          "type": "string",
          "description": "Sku of the product being viewed"
      },
      "category": {
          "type": "string",
          "description": "Category of the product being viewed"
      },
      "name": {
          "type": "string",
          "description": "Name of the product being viewed"
      },
      "brand": {
          "type": "string",
          "description": "Brand of the product being viewed"
      },
      "variant": {
          "type": "string",
          "description": "Variant of the product being viewed"
      },
      "price": {
          "type": "number",
          "description": "Price of the product ($) being viewed"
      },
      "quantity": {
          "type": "integer",
          "description": "Quantity of the product being viewed"
      },
      "coupon": {
          "type": "string",
          "description": "Coupon code associated with a product (for example, MAY_DEALS_3)"
      },
      "position": {
          "type": "integer",
          "description": "Position in the product list (ex. 3)"
      },
      "url": {
          "type": "string",
          "description": "URL of the product being viewed"
      },
      "image_url": {
          "type": "string",
          "description": "URL of the product image being viewed"
      },
  },

  "required": [                    // Required properties
      "product_id",
      "sku",
      "category",
      "name",
      "brand",
      "price",
      "quantity"
  ],
  "additionalProperties": false,   // No additional properties allowed
}
```

</details>
<br>

### Identifying and selecting schemas
Schemas are uniquely identified by their `$id`, which is determine by their path relative to the `schemas/` directory. For example:

| Path to schema                                                      | Schema `$id`                             |
|---------------------------------------------------------------------|------------------------------------------|
| `my-reflekt-project/schemas/segment/ecommerce/CartViewed/1-0.json`  | `segment/ecommerce/CartViewed/1-0.json`  |
| `my-reflekt-project/schemas/segment/ecommerce/LinkClicked/2-1.json` | `segment/ecommerce/LinkClicked/2-1.json` |

These `$id`s are used to `--select` schemas when running Reflekt commands. For example:

```bash
❯ reflekt lint --select segment/ecommerce/CartViewed/1-0.json      # Lint version 1-0 of the CartViewed schema
❯ reflekt lint --select "segment/ecommerce/Link Clicked/2-1.json"  # $ids with spaces must be surrounded by quotes
❯ reflekt lint --select segment/ecommerce                          # Lint all schemas in the segment/ecommerce directory
```

### Schema versions
As data collection requirements change, event schemas must be updated to *reflekt* the new schema. Reflekt supports schema evolution by defining a `version` for each schema, starting at `1-0` and following a `MAJOR-MINOR` version spec. The definition of `MAJOR` and `MINOR` is as follows:

- **MAJOR** - Breaking schema changes incompatible with previous data. Examples:
  - Add/remove/rename a required property
  - Change a property from *optional to required*
  - Change a property's type
- **MINOR** - Non-breaking schema changes compatible with previous data. Examples:
  - Add/remove/rename an optional property
  - Change a property from *required to optional*

When defining a new schema version, **create a new file** with the incremented version and updated schema definition.

### Interacting with schema registries
Schema registries are used to store and serve schemas. Once a schema is in a registry, it can be used to validate event data against the schema to ensure event data quality. Reflekt supports interacting with schema registries to push (publish) and pull (retrieve) schemas. Currently, the following registries are supported:

| **Registry**          | **`--push` support** | **`--pull` support** | **Schema `--select` syntax**            | **Schema `version` support**                                                                                                                                                                                            |
|-----------------------|:--------:|:--------:|----------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Segment Protocols** |     ✅    |     ✅    | `--select segment/tracking_plan_name` | Only supports `MAJOR-0` versions.                                                                                                                                              |
| **Avo**               |     ❌    |     ✅    | `--select avo/branch_name`            | Schema changes managed in Avo [branches](https://www.avo.app/docs/workspace/branches) - `"version": "1-0"` (always).<br> Avo customers pull schemas with `reflekt pull` and build dbt artifacts with `reflekt build`. |

#### Pull schemas from a registry
Pulling schemas from a registry is as easy as ...
```bash
❯ reflekt pull --select segment/ecommerce
[19:28:32] INFO     Running with reflekt=0.3.1

[19:28:32] INFO     Searching Segment for schemas

[19:28:33] INFO     Found 9 schemas to pull:

[19:28:33] INFO     1 of 9 Writing to /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Identify/1-0.json
[19:28:34] INFO     2 of 9 Writing to /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Group/1-0.json
[19:28:34] INFO     3 of 9 Writing to /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Cart Viewed/1-0.json
[19:28:34] INFO     4 of 9 Writing to /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Checkout Started/1-0.json
[19:28:34] INFO     5 of 9 Writing to /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Checkout Step Completed/1-0.json
[19:28:34] INFO     6 of 9 Writing to /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Checkout Step Viewed/1-0.json
[19:28:34] INFO     7 of 9 Writing to /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Order Completed/1-0.json
[19:28:34] INFO     8 of 9 Writing to /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Page Viewed/1-0.json
[19:28:34] INFO     9 of 9 Writing to /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Product Added/1-0.json

[19:28:34] INFO     Completed successfully
```
The `reflekt pull` command builds the corresponding JSON files in the `schemas/` directory. For the example above, the resulting directory structure would be:
```bash
schemas
├── .reflekt
└── segment
    └── ecommerce
        ├── Cart Viewed
        │   └── 1-0.json
        ├── Checkout Started
        │   └── 1-0.json
        ├── Checkout Step Completed
        │   └── 1-0.json
        ├── Checkout Step Viewed
        │   └── 1-0.json
        ├── Group
        │   └── 1-0.json
        ├── Identify
        │   └── 1-0.json
        ├── Order Completed
        │   └── 1-0.json
        ├── Page Viewed
        │   └── 1-0.json
        └── Product Added
            └── 1-0.json
```

#### Push schemas to a registry
Publishing schemas to a registry follows the same pattern ...

```bash
❯ reflekt push --select segment/ecommerce
[19:29:06] INFO     Running with reflekt=0.3.1

[19:29:07] INFO     Searching for JSON schemas in: /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce

[19:29:07] INFO     Found 9 schemas to push

[19:29:07] INFO     1 of 9 Pushing /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Identify/1-0.json
[19:29:07] INFO     2 of 9 Pushing /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Cart Viewed/1-0.json
[19:29:07] INFO     3 of 9 Pushing /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Checkout Step Viewed/1-0.json
[19:29:07] INFO     4 of 9 Pushing /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Group/1-0.json
[19:29:07] INFO     5 of 9 Pushing /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Order Completed/1-0.json
[19:29:07] INFO     6 of 9 Pushing /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Checkout Step Completed/1-0.json
[19:29:07] INFO     7 of 9 Pushing /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Checkout Started/1-0.json
[19:29:07] INFO     8 of 9 Pushing /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Page Viewed/1-0.json
[19:29:07] INFO     9 of 9 Pushing /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Product Added/1-0.json

[19:29:08] INFO     Completed successfully
```

<br>

### Linting schemas
Schemas can be linted to test if they follow the naming and metadata conventions configured for a Reflekt project.

```bash
❯ reflekt lint --select segment/ecommerce
[18:57:45] INFO     Running with reflekt=0.3.1

[18:57:46] INFO     Searching for JSON schemas in: /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce

[18:57:46] INFO     Found 9 schema(s) to lint

[18:57:46] INFO     1 of 9 Linting /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Identify/1-0.json
[18:57:47] INFO     2 of 9 Linting /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Cart Viewed/1-0.json
[18:57:48] ERROR    Property 'cartId' in /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Cart Viewed/1-0.json does not match naming convention 'casing: snake' in
                    /Users/myuser/Repos/my-reflekt-project/reflekt_project.yml.
[18:57:48] INFO     3 of 9 Linting /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Checkout Step Viewed/1-0.json
[18:57:50] INFO     4 of 9 Linting /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Group/1-0.json
[18:57:50] INFO     5 of 9 Linting /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Order Completed/1-0.json
[18:57:54] INFO     6 of 9 Linting /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Checkout Step Completed/1-0.json
[18:57:55] INFO     7 of 9 Linting /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Checkout Started/1-0.json
[18:57:58] INFO     8 of 9 Linting /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Page Viewed/1-0.json
[18:58:01] INFO     9 of 9 Linting /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Product Added/1-0.json

[18:58:04] ERROR    Linting failed with 1 error(s):

[18:58:04] ERROR    Property 'cartId' in /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Cart Viewed/1-0.json does not match naming convention 'casing: snake' in
                    /Users/myuser/Repos/my-reflekt-project/reflekt_project.yml.
```

Running `reflekt lint` in a CI/CD pipeline is a great way to ensure schema consistency and quality before pushing schemas to a schema registry.

<br>

## dbt artifacts
[dbt](https://www.getdbt.com/) is a popular data tool to transformation and model data. When modeling data in dbt, it is [best practice](https://docs.getdbt.com/guides/best-practices/how-we-structure/1-guide-overview) to:
- Define sources pointing to the raw data.
- Define staging models, 1-to-1 for each source, that [rename, recast, or usefully reconsider](https://discourse.getdbt.com/t/how-we-used-to-structure-our-dbt-projects/355#data-transformation-101-1) columns into a consistent format. Materialized as views.
- Document staging models with descriptions for the model and its fields, including relevant tests (e.g., unique and not_null IDs) as required.

While we recommend following this practice, it can be ***a lot of work to maintain*** for product analytics, where:
- There are many events (often 100+) and properties.
- Events and properties are added or updated regularly as the product and data requirements evolve.
- The Product and Engineer teams are bigger than the Data team, making it hard to keep up with the changes.

**Reflekt can help by building dbt artifacts for you with a single CLI command.** Think of this as dbt's [codegen](https://github.com/dbt-labs/dbt-codegen) package on steroids :muscle: :pill:.

### Building private dbt packages
To build a private dbt package with sources, staging models, and docs that perfectly *reflekts* the schemas in a Reflekt project and the raw data in the warehouse, you can run a command like the example below.

Where:
- `--select segment/ecommerce` selects all the schemas in the `schemas/segment/ecommerce/` directory.
- `--source snowflake.raw.ecomm_demo` specifies to connect to a data source with ID `snowflake`, database `raw`, and schema `ecomm_demo` as defined in `reflekt_profiles.yml`.
- `--sdk segment` specifies the event data was collected via the Segment SDK. Reflekt knows how Segment loads data into data warehouses and writes SQL models accordingly.

If an event schema has multiple versions, Reflekt builds a staging model for both versions, allowing the Data team to easily consolidate schema changes as needed.

```bash
❯ reflekt build dbt --select segment/ecommerce --source snowflake.raw.ecomm_demo --sdk segment
[09:45:23] INFO     Running with reflekt=0.3.1

[09:45:24] INFO     Searching for JSON schemas in: /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce

[09:45:24] INFO     Found 10 schemas to build

[09:45:24] INFO     Building dbt package:
                        name: reflekt_demo
                        dir: /Users/myuser/Repos/my-reflekt-project/artifacts/dbt/reflekt_demo
                        --select: segment/ecommerce
                        --sdk_arg: segment
                        --source: snowflake.raw.ecomm_demo

[09:45:24] INFO     Building dbt source 'ecomm_demo'
[09:45:24] INFO     Building dbt artifacts for schema: /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Identify/1-0.json
[09:45:26] INFO     Building dbt table 'identifies' in source 'ecomm_demo'
[09:45:26] INFO     Building staging model 'stg_ecomm_demo__identifies.sql'
[09:45:26] INFO     Building dbt documentation '_stg_ecomm_demo__identifies.yml'

[09:45:26] INFO     Building dbt artifacts for schema: Segment 'users' table
[09:45:26] INFO     Building dbt table 'users' in source 'ecomm_demo'
[09:45:26] INFO     Building staging model 'stg_ecomm_demo__users.sql'
[09:45:26] INFO     Building dbt documentation '_stg_ecomm_demo__users.yml'

[09:45:26] INFO     Building dbt artifacts for schema: /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Cart Viewed/2-0.json
[09:45:26] INFO     Building dbt table 'cart_viewed' in source 'ecomm_demo'
[09:45:26] INFO     Building staging model 'stg_ecomm_demo__cart_viewed__v2_0.sql'
[09:45:26] INFO     Building dbt documentation '_stg_ecomm_demo__cart_viewed__v2_0.yml'

[09:45:26] INFO     Building dbt artifacts for schema: /Users/myuser/Repos/my-reflekt-project/schemas/segment/ecommerce/Cart Viewed/1-0.json
[09:45:27] INFO     Building staging model 'stg_ecomm_demo__cart_viewed.sql'
[09:45:27] INFO     Building dbt documentation '_stg_ecomm_demo__cart_viewed.yml'

...
...  # Full output omitted for brevity
...

[09:45:29] INFO     Building dbt artifacts for schema: Segment 'tracks' table
[09:45:29] INFO     Building dbt table 'tracks' in source 'ecomm_demo'
[09:45:29] INFO     Building staging model 'stg_ecomm_demo__tracks.sql'
[09:45:29] INFO     Building dbt documentation '_stg_ecomm_demo__tracks.yml'


[09:45:29] INFO     Copying dbt package from temporary path /Users/myuser/Repos/my-reflekt-project/.reflekt_cache/artifacts/dbt/reflekt_demo to
                    /Users/myuser/Repos/my-reflekt-project/artifacts/dbt/reflekt_demo

[09:45:29] INFO     Successfully built dbt package
```

### Using private dbt packages
To use a Reflekt dbt package in a downstream dbt project, add it to the dbt project's `packages.yml`.

#### dbt-core
```yaml
# packages.yml
packages:
  - git: "https://github.com/<your_user_or_org>/<your_repo>"  # Reflekt project Github repo URL
    subdirectory: "dbt-packages/<reflekt_dbt_package_name>"
    revision: v0.1.0__reflekt_demo  # Branch, tag, or commit (40-character hash). For latest, use 'main' branch.
```

#### dbt-cloud
```yaml
# packages.yml
packages:
  - git: ""https://{{env_var('DBT_ENV_SECRET_GITHUB_PAT')}}@github.com/<your_user_or_org>/<your_repo>.git""  # Reflekt project Github repo URL with GitHub PAT
    subdirectory: "dbt-packages/<reflekt_dbt_package_name>"
    revision: v0.1.0__reflekt_demo  # Branch, tag, or commit (40-character hash). For latest, use 'main' branch.
```
To use with dbt-cloud, you will need to create a [Github personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) (e.g., `DBT_ENV_SECRET_GITHUB_PAT`) and [configure it as an environment variable](https://docs.getdbt.com/docs/dbt-cloud/using-dbt-cloud/cloud-environment-variables) in your dbt-cloud account.

For local dbt development, set the environment variable on your local machine.
```bash
# Add the following line to your .zshrc, .bash_profile, etc.
export DBT_ENV_SECRET_GITHUB_PAT=YOUR_TOKEN
```

### Supported data warehouses
Reflekt currently supports the following data warehouses:
- Snowflake
- Redshift
- :construction: BigQuery support coming soon! :construction:
