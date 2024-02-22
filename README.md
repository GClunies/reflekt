<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt
> /rəˈflek(t)/ - _to embody or represent in a faithful or appropriate way_

![PyPI](https://img.shields.io/pypi/v/reflekt?style=for-the-badge)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/reflekt?style=for-the-badge)
![GitHub](https://img.shields.io/github/license/gclunies/reflekt?style=for-the-badge)

Reflekt helps teams design, govern, and model event data for warehouse-first product analytics - integrating with [Customer Data Platforms](#customer-data-platform-cdp), [Schema Registries](#schema-registry), [Data Warehouses](#data-warehouse), and [dbt](#dbt). Events schemas are designed with `code` using [JSON schema](https://json-schema.org/), version controlled, and updated via pull requests (PRs), enabling:
  - Branches for parallel development and testing.
  - Reviews and discussion amongst teams and stakeholders.
  - CI/CD suites to:
    - `reflekt lint` schemas against naming and metadata rules.
    - `reflekt push` schemas to deploy them to a [schema registry](#schema-registry) for event data validation.

Stop writing SQL & YAML for event data. `reflekt build` a [dbt](#dbt) package to model, document, and test events in the warehouse.

![reflekt build](docs/reflekt_build.gif)

To see `reflekt` in action, checkout:
- Demo [video](https://www.loom.com/share/75b60cfc2b3549edafde4eedcb3c9631?sid=fb610521-c651-40f9-9de5-8f07a2534302)
- Demo [reflekt-jaffle-shop](https://github.com/GClunies/reflekt-jaffle-shop/) project

## Getting Started
### Install
Reflekt is available on [PyPI](https://pypi.org/project/reflekt/). Install with `pip` or your preferred package manager, preferably in a virtual environment:
```bash
❯ source /path/to/venv/bin/activate  # Activate virtual environment
❯ pip install reflekt                # Install Reflekt
❯ reflekt --version                  # Confirm installation
Reflekt CLI Version: 0.3.1
```

### Create a Reflekt Project
To create a new Reflekt project: create a new directory, initialize a Git repo, and run `reflekt init`.
```bash
❯ mkdir ~/Repos/my-reflekt-project  # Create a new directory for the project
❯ cd ~/Repos/my-reflekt-project     # Navigate to the project directory
❯ git init                          # Initialize a new Git repo (REQUIRED)
❯ reflekt init                      # Initialize a new Reflekt project in the current directory

# Follow the prompts to configure the project
```

This will create a new Reflekt project with the following structure:
```bash
my-reflekt-project
├── .logs/                # CLI command logs
├── .reflekt_cache/       # Local cache used by CLI
├── artifacts/            # Data artifacts from `reflekt build`
├── schemas/              # Event schema definitions
├── .gitignore
├── README.md
└── reflekt_project.yml   # Project configuration
```

### Configure a Reflekt Project
Reflekt uses 3 files to define and configure a Reflekt project.
| Configuration File               | Purpose |
|----------------------------------|---------|
| `reflekt_project.yml`            | Project settings, event and property conventions, data artifact generation, <br>additional Avo registry config (optional) |
| `reflekt_profiles.yml`           | Connection details to schema registries and data warehouses. |
| `schemas/.reflekt/meta/1-0.json` | Meta-schema used to:<br> 1. Events in `schemas/` follow the Reflekt format.<br> 2. Define global `"metadata": {}` requirement for all schemas.  |

> [!TIP]
> Click the example configuration files below to see their structure and settings.

<details>
<summary>Example: <code>reflekt_project.yml</code></summary>
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

<details>
<summary>Example: <code>reflekt_profiles.yml</code></summary>
<br>

```yaml
# Example reflekt_profiles.yml
version: 1.0

dev_reflekt:                                         # Profile name (multiple allowed)
  registry:                                          # Schema registry connection details (multiple allowed)
    - type: segment
      api_token: segment_api_token                   # https://docs.segmentapis.com/tag/Getting-Started#section/Get-an-API-token

    - type: avo
      workspace_id: avo_workspace_id                 # https://www.avo.app/docs/public-api/export-tracking-plan#endpoint
      service_account_name: avo_service_account_name # https://www.avo.app/docs/public-api/authentication#creating-service-accounts
      service_account_secret: avo_service_account_secret

  source:                          # Data warehouse connection details (multiple allowed)
    - id: snowflake                # ID must be unique per profile
      type: snowflake              # Specify details where raw event data is stored
      account: abc12345
      database: raw
      warehouse: transforming
      role: transformer
      user: reflekt_user           # Create reflekt_user with access to raw data (permissions: USAGE, SELECT)
      password: reflekt_user_password

    - id: redshift                 # ID must be unique per profile
      type: redshift               # Specify details where raw event data is stored
      host: example-redshift-cluster-1.abc123.us-west-1.redshift.amazonaws.com
      database: analytics
      port: 5439
      user: reflekt_user           # Create reflekt_user with access to raw data (permissions: USAGE, SELECT)
      password: reflekt_user_password

    - id: bigquery                 # ID must be unique per profile
      type: bigquery               # Specify details where raw event data is stored
      project: raw-data
      dataset: jaffle_shop_segment
      keyfile_json:                # Create a reflekt-user service account with access to BigQuery project where raw event data lands (permissions: BigQuery Data Viewer, BigQuery Job User). Include JSON keyfile fields below.
        type: "service_account"
        project_id: "foo-bar-123456"
        private_key_id: "abc123def456ghi789"
        private_key: "-----BEGIN PRIVATE KEY-----\nmy-very-long-private-keyF\n\n-----END PRIVATE KEY-----\n"
        client_email: "reflekt-user@foo-bar-123456.iam.gserviceaccount.com"
        client_id: "123456789101112131415161718"
        auth_uri: "https://accounts.google.com/o/oauth2/auth"
        token_uri: "https://oauth2.googleapis.com/token"
        auth_provider_x509_cert_url: "https://www.googleapis.com/oauth2/v1/certs"
        client_x509_cert_url: "https://www.googleapis.com/robot/v1/metadata/x509/reflekt-user%40foo-bar-123456.iam.gserviceaccount.com"
```
</details>

<details>
<summary>Example: <code>schemas/.reflekt/meta/1-0.json</code></summary>
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

### Defining Event Schemas
Events in a Reflekt project are defined using the [JSON schema](https://json-schema.org/) specification and are stored in the `schemas/` directory of the project.

> [!TIP]
> Click to expand the `Order Completed` example below.

<details>
<summary>Example: <code>my-reflekt-project/schemas/jaffle_shop/Order_Completed/1-0.json</code></summary>
<br>

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "jaffle_shop/Order_Completed/1-0.json",  // Unique ID for schema (relative to `schemas/` dir)
    "description": "User completed an order (i.e., user confirmed and payment was successful).",
    "self": {
        "vendor": "com.thejaffleshop", // Company, application, team, or system that authored the schema
        "name": "Order Completed",     // Name of the event
        "format": "jsonschema",        // Format of the schema
        "version": "1-0",              // Version of the schema
        "metadata": {                  // Metadata for the event
            "code_owner": "@the-jaffle-shop/frontend-guild",
            "product_owner": "pmanager@thejaffleshop.com",
        }
    },
    "type": "object",
    "properties": {
        "coupon": {
            "description": "Coupon code used for the order.",
            "type": [
                "string",
                "null"
            ]
        },
        "currency": {
            "description": "Currency for the order.",
            "type": "string"
        },
        "discount": {
            "description": "Total discount for the order.",
            "type": "number"
        },
        "order_id": {
            "description": "Unique identifier for the order.",
            "type": "string"
        },
        "products": {
            "description": "List of products in the cart.",
            "items": {
                "additionalProperties": false,
                "properties": {
                    "category": {
                        "description": "Category of the product.",
                        "type": "string"
                    },
                    "name": {
                        "description": "Name of the product.",
                        "type": "string"
                    },
                    "price": {
                        "description": "Price of the product.",
                        "type": "number"
                    },
                    "product_id": {
                        "description": "Unique identifier for the product.",
                        "type": "string"
                    },
                    "quantity": {
                        "description": "Quantity of the product in the cart.",
                        "type": "integer"
                    },
                    "sku": {
                        "description": "Stock keeping unit for the product.",
                        "type": "string"
                    }
                },
                "required": [
                    "product_id",
                    "sku",
                    "category",
                    "name",
                    "price",
                    "quantity"
                ],
                "type": "object"
            },
            "type": "array"
        },
        "revenue": {
            "description": "Total revenue for the order.",
            "type": "number"
        },
        "session_id": {
            "description": "Unique identifier for the session.",
            "type": "string"
        },
        "shipping": {
            "description": "Shipping cost for the order.",
            "type": "number"
        },
        "subtotal": {
            "description": "Subtotal for the order (revenue - discount).",
            "type": "number"
        },
        "tax": {
            "description": "Tax for the order.",
            "type": "number"
        },
        "total": {
            "description": "Total cost for the order (revenue - discount + shipping + tax = subtotal + shipping + tax).",
            "type": "number"
        }
    },
    "required": [
        "session_id",
        "order_id",
        "revenue",
        "coupon",
        "discount",
        "subtotal",
        "shipping",
        "tax",
        "total",
        "currency",
        "products"
    ],
    "additionalProperties": false
}
```
</details>


#### Schema `$id` and `version`
Schemas in a Reflekt project are identified and `--select`ed by their `$id`, which is their path relative to the `schemas/` directory. For example:
| File Path to Schema                                                   | Schema `$id`                       |
|-----------------------------------------------------------------------|------------------------------------|
| `~/repos/my-reflekt-project/schemas/jaffle_shop/Cart_Viewed/1-0.json` | `jaffle_shop/Cart_Viewed/1-0.json` |
| `~/repos/my-reflekt-project/schemas/jaffle_shop/Cart_Viewed/2-1.json` | `jaffle_shop/Cart_Viewed/2-1.json` |

Each schema has a `version` (e.g., `1-0`, `2-1`), used to indicate changes to data collection requirements. New event schemas start at `1-0` and follow a `MAJOR-MINOR` version spec, as shown in the table below.
| Type  | Description | Example | Use Case |
|-------|---------------------------------------------------|---------|----------|
| MAJOR | Breaking change incompatible with previous data. | `1-0`, `2-0`<br>(ends in `-0) | - Add/remove/rename a *required* property<br> - Change a property from *optional to required*<br> - Change a property's type |
| MINOR | Non-breaking change compatible with previous data. | `1-1`, `2-3` | - Add/remove/rename an *optional* property<br> - Change a property from *required to optional* |

> [!NOTE]
> For `MINOR` schema versions (non-breaking changes), you can either:
> - Update the existing schema and increment the MINOR version number.
> - Create a new `.json` file with the updated schema and increment the MINOR version number.
>
> For `MAJOR` schema versions (breaking changes), you MUST:
> - **Create a new `.json` file** with the updated schema. This way, an application/product/feature can begin using the new schema while others continue to use the old schema (migrating later).

### Linting Event Schemas
Schemas can be linted to test if they follow the naming conventions in your [`reflekt_project.yml`] and metadata conventions in `schemas/.reflekt/meta/1-0.json`.

```bash
❯ reflekt lint --select schemas/jaffle_shop
[18:31:12] INFO     Running with reflekt=0.5.0
[18:31:12] INFO     Searching for JSON schemas in: /Users/gclunies/Repos/reflekt/schemas/jaffle_shop
[18:31:12] INFO     Found 9 schema(s) to lint
[18:31:12] INFO     1 of 9 Linting /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Order_Completed/1-0.json
[18:31:19] INFO     2 of 9 Linting /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Identify/1-0.json
[18:31:20] INFO     3 of 9 Linting /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Product_Clicked/1-0.json
[18:31:24] INFO     4 of 9 Linting /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Cart_Viewed/1-0.json
[18:31:26] INFO     5 of 9 Linting /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Product_Removed/1-0.json
[18:31:32] INFO     6 of 9 Linting /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Product_Added/1-0.json
[18:31:37] INFO     7 of 9 Linting /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Checkout_Step_Viewed/1-0.json
[18:31:40] INFO     8 of 9 Linting /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Checkout_Step_Completed/1-0.json
[18:31:44] INFO     9 of 9 Linting /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Page_Viewed/1-0.json
[18:31:51] INFO     Completed successfully
```

### Sending Event Schemas to a Schema Registries
In order to validate events as they flow from **Application -> Registry -> Customer Data Platform (CDP) -> Data Warehouse**, we need to send a copy of our event schemas to a schema registry (see [supported registries](#schema-registry)). This is done with the `reflekt push` command.

```bash
❯ reflekt push --registry segment --select schemas/jaffle_shop
[18:41:05] INFO     Running with reflekt=0.5.0
[18:41:06] INFO     Searching for JSON schemas in: /Users/gclunies/Repos/reflekt/schemas/jaffle_shop
[18:41:06] INFO     Found 9 schemas to push
[18:41:06] INFO     1 of 9 Pushing /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Order_Completed/1-0.json
[18:41:06] INFO     2 of 9 Pushing /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Identify/1-0.json
[18:41:06] INFO     3 of 9 Pushing /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Product_Clicked/1-0.json
[18:41:06] INFO     4 of 9 Pushing /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Cart_Viewed/1-0.json
[18:41:06] INFO     5 of 9 Pushing /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Product_Removed/1-0.json
[18:41:06] INFO     6 of 9 Pushing /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Product_Added/1-0.json
[18:41:06] INFO     7 of 9 Pushing /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Checkout_Step_Viewed/1-0.json
[18:41:06] INFO     8 of 9 Pushing /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Checkout_Step_Completed/1-0.json
[18:41:06] INFO     9 of 9 Pushing /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Page_Viewed/1-0.json
[18:41:08] INFO     Completed successfully
```

### Building `dbt` packages to Model Event Data
Modeling event data in `dbt` a lot of work. Do we want staging models that are clean, documented, and tested? **OF COURSE!**

Do we want to write and maintain SQL and YAML docs for hundreds of events? **ABSOLUTELY NOT!**

You no longer have to choose between speed and best practice. Automate writing SQL for staging models and YAML for documentation and testing, packaged up in your very own provate dbt package. All you need is a single CLI command.

```bash
❯ reflekt build --artifact dbt --select schemas/jaffle_shop --source snowflake.raw.jaffle_shop_segment --sdk segment
[18:56:25] INFO     Running with reflekt=0.5.0
[18:56:26] INFO     Searching for JSON schemas in: /Users/gclunies/Repos/reflekt/schemas/jaffle_shop
[18:56:26] INFO     Found 9 schemas to build
[18:56:27] INFO     Building dbt package:
                        name: jaffle_shop
                        dir: /Users/gclunies/Repos/reflekt/artifacts/dbt/jaffle_shop
                        --select: jaffle_shop
                        --sdk_arg: segment
                        --source: snowflake.raw.jaffle_shop_segment
[18:56:27] INFO     Building dbt source 'jaffle_shop_segment'
[18:56:27] INFO     Building dbt artifacts for schema: /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Order_Completed/1-0.json
[18:56:28] INFO     Building dbt table 'order_completed' in source 'jaffle_shop_segment'
[18:56:28] INFO     Building staging model 'stg_jaffle_shop_segment__order_completed.sql'
[18:56:28] INFO     Building dbt documentation '_stg_jaffle_shop_segment__order_completed.yml'
[18:56:28] INFO     Building dbt artifacts for schema: /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Identify/1-0.json
[18:56:29] INFO     Building dbt table 'identifies' in source 'jaffle_shop_segment'
[18:56:29] INFO     Building staging model 'stg_jaffle_shop_segment__identifies.sql'
[18:56:29] INFO     Building dbt documentation '_stg_jaffle_shop_segment__identifies.yml'
[18:56:29] INFO     Building dbt artifacts for schema: Segment 'users' table
[18:56:29] INFO     Building dbt table 'users' in source 'jaffle_shop_segment'
[18:56:29] INFO     Building staging model 'stg_jaffle_shop_segment__users.sql'
[18:56:29] INFO     Building dbt documentation '_stg_jaffle_shop_segment__users.yml'
[18:56:29] INFO     Building dbt artifacts for schema: /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Product_Clicked/1-0.json
[18:56:29] INFO     Building dbt table 'product_clicked' in source 'jaffle_shop_segment'
[18:56:29] INFO     Building staging model 'stg_jaffle_shop_segment__product_clicked.sql'
[18:56:29] INFO     Building dbt documentation '_stg_jaffle_shop_segment__product_clicked.yml'
[18:56:29] INFO     Building dbt artifacts for schema: /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Cart_Viewed/1-0.json
[18:56:29] INFO     Building dbt table 'cart_viewed' in source 'jaffle_shop_segment'
[18:56:29] INFO     Building staging model 'stg_jaffle_shop_segment__cart_viewed.sql'
[18:56:29] INFO     Building dbt documentation '_stg_jaffle_shop_segment__cart_viewed.yml'
[18:56:29] INFO     Building dbt artifacts for schema: /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Product_Removed/1-0.json
[18:56:30] INFO     Building dbt table 'product_removed' in source 'jaffle_shop_segment'
[18:56:30] INFO     Building staging model 'stg_jaffle_shop_segment__product_removed.sql'
[18:56:30] INFO     Building dbt documentation '_stg_jaffle_shop_segment__product_removed.yml'
[18:56:30] INFO     Building dbt artifacts for schema: /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Product_Added/1-0.json
[18:56:30] INFO     Building dbt table 'product_added' in source 'jaffle_shop_segment'
[18:56:30] INFO     Building staging model 'stg_jaffle_shop_segment__product_added.sql'
[18:56:30] INFO     Building dbt documentation '_stg_jaffle_shop_segment__product_added.yml'
[18:56:30] INFO     Building dbt artifacts for schema: /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Checkout_Step_Viewed/1-0.json
[18:56:30] INFO     Building dbt table 'checkout_step_viewed' in source 'jaffle_shop_segment'
[18:56:30] INFO     Building staging model 'stg_jaffle_shop_segment__checkout_step_viewed.sql'
[18:56:30] INFO     Building dbt documentation '_stg_jaffle_shop_segment__checkout_step_viewed.yml'
[18:56:30] INFO     Building dbt artifacts for schema: /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Checkout_Step_Completed/1-0.json
[18:56:30] INFO     Building dbt table 'checkout_step_completed' in source 'jaffle_shop_segment'
[18:56:30] INFO     Building staging model 'stg_jaffle_shop_segment__checkout_step_completed.sql'
[18:56:30] INFO     Building dbt documentation '_stg_jaffle_shop_segment__checkout_step_completed.yml'
[18:56:30] INFO     Building dbt artifacts for schema: /Users/gclunies/Repos/reflekt/schemas/jaffle_shop/Page_Viewed/1-0.json
[18:56:30] INFO     Building dbt table 'pages' in source 'jaffle_shop_segment'
[18:56:30] INFO     Building staging model 'stg_jaffle_shop_segment__pages.sql'
[18:56:30] INFO     Building dbt documentation '_stg_jaffle_shop_segment__pages.yml'
[18:56:30] INFO     Building dbt artifacts for schema: Segment 'tracks' table
[18:56:31] INFO     Building dbt table 'tracks' in source 'jaffle_shop_segment'
[18:56:31] INFO     Building staging model 'stg_jaffle_shop_segment__tracks.sql'
[18:56:31] INFO     Building dbt documentation '_stg_jaffle_shop_segment__tracks.yml'
[18:56:31] INFO     Copying dbt package from temporary path /Users/gclunies/Repos/reflekt/.reflekt_cache/artifacts/dbt/jaffle_shop to /Users/gclunies/Repos/reflekt/artifacts/dbt/jaffle_shop
[18:56:31] INFO     Successfully built dbt package
```

---

## CLI Commands
A general description of commands can be seen by running `reflekt --help`. For ease, the help page for each CLI command is shown below.

### `reflekt init`
```bash
❯ reflekt init --help
[11:17:16] INFO     Running with reflekt=0.6.0

 Usage: reflekt init [OPTIONS]

 Initialize a Reflekt project.

╭─ Options ──────────────────────────────────────────────────────╮
│ --dir                        TEXT  [default: .]                │
│ --verbose    --no-verbose          [default: no-verbose]       │
│ --help                             Show this message and exit. │
╰────────────────────────────────────────────────────────────────╯
```

### `reflekt debug`
```bash
❯ reflekt debug --help
[11:18:07] INFO     Running with reflekt=0.6.0

 Usage: reflekt debug [OPTIONS]

 Check Reflekt project configuration.

╭─ Options ───────────────────────────────────╮
│ --help          Show this message and exit. │
╰─────────────────────────────────────────────╯
```

### `reflekt lint`
```bash
❯ reflekt lint --help
[11:20:29] INFO     Running with reflekt=0.6.0

 Usage: reflekt lint [OPTIONS]

 Lint schema(s) to test for naming and metadata conventions.

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --select   -s      TEXT  Schema(s) to lint. Starting with 'schemas/' is optional. [default: None] [required] │
│    --verbose  -v            Verbose logging.                                                                        │
│    --help                   Show this message and exit.                                                             │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### `reflekt push`
```bash
❯ reflekt push --help
[11:22:37] INFO     Running with reflekt=0.6.0

 Usage: reflekt push [OPTIONS]

 Push schema(s) to a schema registry.

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --registry  -r      [avo|segment]  Schema registry to push to. [default: None] [required]                                          │
│ *  --select    -s      TEXT           Schema(s) to push to schema registry. Starting with 'schemas/' is optional. [default: None] │
│    --delete    -D                     Delete schema(s) from schema registry. Prompts for confirmation                                 │
│    --force     -F                     Force command to run without confirmation.                                                      │
│    --profile   -p      TEXT           Profile in reflekt_profiles.yml to use for schema registry connection.                          │
│    --verbose   -v                     Verbose logging.                                                                                │
│    --help                             Show this message and exit.                                                                     │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### `reflekt pull`
```bash
❯ reflekt pull --help
[11:25:18] INFO     Running with reflekt=0.6.0

 Usage: reflekt pull [OPTIONS]

 Pull schema(s) from a schema registry.

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --registry  -r      [avo|segment]  Schema registry to pull from. [default: None] [required]                                                                         │
│ *  --select    -s      TEXT           Schema(s) to pull from schema registry. If registry uses tracking plans, starting with the plan name. [default: None] [required] │
│    --profile   -p      TEXT           Profile in reflekt_profiles.yml to use for schema registry connection.                                                           │
│    --verbose   -v                     Verbose logging.                                                                                                                 │
│    --help                             Show this message and exit.                                                                                                      │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### `reflekt build`
```bash
❯ reflekt build --help
[11:31:36] INFO     Running with reflekt=0.6.0

 Usage: reflekt build [OPTIONS]

 Build data artifacts based on schemas.

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --artifact  -a      [dbt]      Type of data artifact to build. [default: None] [required]                                                                                                         │
│ *  --select    -s      TEXT       Schema(s) to build data artifacts for. Starting with 'schemas/' is optional. [default: None] [required]                                                            │
│ *  --sdk               [segment]  The SDK used to collect the event data. [default: None] [required]                                                                                                 │
│ *  --source            TEXT       The <source_id>.<database>.<schema> storing raw event data. <source_id> must be a data warehouse source defined in reflekt_profiles.yml [default: None] [required] │
│    --profile   -p      TEXT       Profile in reflekt_profiles.yml to look for the data source specified by the --source option. Defaults to default_profile in reflekt_project.yml                   │
│    --verbose   -v                 Verbose logging.                                                                                                                                                   │
│    --help                         Show this message and exit.                                                                                                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

---

## Integrations

### Customer Data Platform (CDP)
Reflekt understands how popular Customer Data Platforms (CDPs) collect event data and load it into data warehouses. This understanding allows Reflekt to:
  - Parse the schemas in a Reflekt project.
  - Find matching tables for events in the data warehouse.
  - Automate writing a private dbt package that creates sources, staging models, and documentation for event data.

| CDP | Supported |
|-----|-----------|
| [Segment](https://segment.com/) | ✅ |
| [Rudderstack](https://www.rudderstack.com/) | 🚧 Coming Soon 🚧 |
| [Amplitude](https://amplitude.com/) | 🚧 Coming Soon 🚧  |


### Schema Registry
Schema registries store and serve schemas. Once a schema is registered with a registry, it can be used to validate events to ensure data quality. Reflekt works with schema registries from CDPs, SaaS vendors, and open-source projects - allowing teams to decide between managed and self-hosted solutions.

| Registry | Cost | Open Source | Schema Versions | Recommended Workflow |
|----------|------|-------------|------------------------|-----------------|
| [Segment Protocols](https://segment.com/docs/protocols/) | Pricing | ❌ | `MAJOR` only | Manage schemas in Reflekt.<br> `reflekt push` to Protocols for event validation.<br> `reflekt build --artifact dbt` to build dbt package. |
| [Avo](https://www.avo.app/) | Pricing | ❌ | `MAJOR` only | Manage schemas in Avo.<br> `reflekt pull` to get schemas.<br>  `reflekt build --artifact dbt` to build dbt package. |
| [reflekt-registry](https://github.com/GClunies/reflekt-registry)<br> 🚧 Coming Soon 🚧 | Free | ✅ | `MAJOR` & `MINOR` |  Manage schemas in Reflekt.<br> `reflekt push` to reflekt-registry.<br> `reflekt build --artifact dbt` to build dbt package. |

### Data Warehouse
In order to find tables and columns that match event schemas and their properties, Reflekt needs to connect to a cloud data warehouse where raw evetn data is stored.

| Data Warehouse | Supported |
|----------------|-----------|
| [Snowflake](https://www.snowflake.com/) | ✅ |
| [Redshift](https://aws.amazon.com/redshift/) | ✅ |
| [BigQuery](https://cloud.google.com/bigquery) | ✅ |

> [!NOTE]
> Reflekt **NEVER** copies, moves, or modifies your events in the data warehouse. It has no visibility into your data.<br>
> It ONLY reads table and column names for artifact templating.

### dbt
[dbt](https://www.getdbt.com/) is a data transformation tool that enables anyone who knows SQL to transform (model) data in a cloud data warehouse. When modeling data in dbt, it is [best practice](https://docs.getdbt.com/guides/best-practices/how-we-structure/1-guide-overview) to:
- Define sources pointing to the raw data.
- Define staging models, 1-to-1 for each source, that [rename, recast, or usefully reconsider](https://discourse.getdbt.com/t/how-we-used-to-structure-our-dbt-projects/355#data-transformation-101-1) columns into a consistent format. Materialized as views.
- Document staging models.
- Test the staging models (e.g., unique values, check for nulls, etc).

For product analytics, this can be ***a lot of work to maintain***, where:
- There 10s to 100s of events and properties.
- Events and properties are added/updated as requirements evolve, often without the Data team knowing.
- Product and Engineering teams are bigger than the Data team, making it account for data changes in models and documentation.

`reflekt build` handles all of this by automating the creation of private dbt package that creates sources, staging models, and documentation for each event with a schema in a Reflekt project. This private package can be used as a foundation for warehouse first product analytics.

## Contribute
- Source Code: [github.com/GClunies/reflekt](https://github.com/GClunies/reflekt)
- Issue Tracker: [github.com/GClunies/reflekt/issues](https://github.com/GClunies/reflekt/issues)
- Pull Requests: [github.com/GClunies/reflekt/pulls](https://github.com/GClunies/reflekt/pulls)

## License
This project is [licensed](LICENSE) under the Apache-2.0 License.

> [!NOTE]
> Reflekt uses `reuse` to attribute licenses for every line of code, recognizing the work of others and ensuring compliance with the licenses of any software used.
