<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt
![PyPI](https://img.shields.io/pypi/v/reflekt?style=for-the-badge)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/reflekt?style=for-the-badge)
![GitHub](https://img.shields.io/github/license/gclunies/reflekt?style=for-the-badge)

A CLI tool to help Data, Engineering, and Product teams:
- Define event schemas as `code` using [JSONschema](https://json-schema.org/), providing a version controlled source of truth.
- Lint schemas to enforce agreed-upon conventions (configurable). Run `reflekt lint` in a CI/CD pipeline to check:
    - Naming conventions (snake_case, camelCase, Title Case, etc.)
    - Descriptions are always included.
    - Required metadata is defined.
- Interact with schema registries
  - Push schema(s) from a Reflekt project to a schema registry where they can be used for event data validation.
  - Pull schema(s) from a schema registry into a Reflekt project to build corresponding data artifacts.
- Build data artifacts (e.g., dbt packages) based on schemas that model and document event data.
  - Keep data artifacts in sync with instrumentation - ready for use by engineers, analysts, and the business.
  - Reduce errors, improve data quality, and automate important (but boring) data tasks.


https://user-images.githubusercontent.com/28986302/217134526-df83ec90-86f3-491e-9588-b7cd56956db1.mp4


## Table of Contents
  - [Installation](#installation)
  - [Commands](#commands)
  - [Reflekt Project Setup](#reflekt-project-setup)
  - [Schemas](#schemas)
  - [Using Data Artifacts](#using-data-artifacts)


## Installation
Reflekt is available on [PyPI](https://pypi.org/project/reflekt/). Install with `pip`:
```bash
pip install reflekt
```


## Commands
A list of CLI commands and arguments can be accessed by running `reflekt --help`. Each Command has a `--help` flag to provide command details (arguments, options, etc.). All commands (except `init`) can be run against a single or multiple schema(s). The command examples below give an overview of the syntax.

See the [argument syntax](#argument-syntax) section for more details on selecting [schemas](#--select), specifying [sources](#--source) and [SDKs](--sdk) used to collect event data.

### `init`
Initialize a Reflekt project.
```bash
reflekt init --dir /path/to/project
```

### `pull`
Pull schemas from a schema registry and create the corresponding structure in project `schemas/` directory.
```bash
# Pull all schemas from 'ecommerce' tracking plan in Segment to schemas/segment/ecommerce/
reflekt pull --select segment/ecommerce/
```
Supported registries: [Segment](https://segment.com/), [Avo](https://avo.app/)

### `push`
Push schemas in project `schemas/` directory to a schema registry.
```bash
# Push all schemas in schemas/segment/ecommerce/ to Segment tracking plan 'ecommerce'
reflekt push --select segment/ecommerce/CartViewed
```
Supported registries: [Segment](https://segment.com/)

### `lint`
Lint schemas in project `schemas/` directory.
```bash
# Lint a single schema (.json is optional)
reflekt lint --select segment/ecommerce/CartViewed/1-0.json
```
Linting checks include:
- Event and property names match the configured naming conventions in `reflekt_project.yml`.
- Only valid data types are used (e.g., disallow `null` or `any` types).
- Descriptions are included for all events and properties.
- Event schema validates against the meta-schema `schemas/.reflekt/event-meta/1-0.json`, enforcing any required metadata.

### `build`
Build a data artifacts based on events schemas. Save time, reduce errors, and improve data quality by ensuring models and documentation are always up-to-date with the latest version of event schemas.

```bash
# Build a dbt package for:
#   - Events collected using the Segment SDK
#   - Event schemas defined in my_reflekt_project/schemas/segment/ecommerce/
#   - Raw event data stored at specified source (snowflake.raw.segment_prod)
reflekt build dbt --select segment/ecommerce --source snowflake.raw.segment_prod --sdk segment
```
**Supported data artifacts:**
- [dbt packages](https://docs.getdbt.com/docs/build/packages) - defines dbt sources, models, and documentation for selected schemas and event data found in the specified [--source](#sources).


## Reflekt Project Setup

### Project Structure
A Reflekt project is a Git repo with the following directory structure:
```
demo_reflekt_project
├── .logs/                # Reflekt command logs
├── .reflekt_cache/       # Local cache used by Reflekt
├── artifacts/            # Data artifacts are built here
├── schemas/              # Event schemas are defined here
├── .gitignore
├── README.md
└── reflekt_project.yml   # Project configuration
```
You can use the `reflekt init` command to create a new Reflekt project. Sync the project to Github to enable collaboration and version control amongst your teams.

### Configuration Files
There are 2 configuration files required to run Reflekt.

#### `reflekt_project.yml`
General project settings, schema & linting conventions, data artifacts configuration.

<details>
<summary><code>example_reflekt_project.yml</code>(click to expand)</summary>
<br>

```yaml
# Example reflekt_project.yml
# GENERAL CONFIG ----------------------------------------------------------------------
version: 1.0

name: reflekt_demo               # Project name
vendor: com.company_name         # Default vendor for schemas in reflekt project
default_profile: dev_reflekt     # Default profile to use from reflekt_profiles.yml
# profiles_path: optional/path/to/reflekt_profiles.yml  # Optional, defaults to ~/.reflekt/reflekt_profiles.yml

# SCHEMAS CONFIG ----------------------------------------------------------------------
schemas:                        # Define schema conventions
  conventions:
    event:
      casing: title             # title | snake | camel | any
      capitalize_camel: true    # Only used if 'casing: camel'
      numbers: false            # Allow numbers in event names
      reserved: []              # Reserved event names
    property:
      casing: snake             # title | snake | camel | any
      capitalize_camel: true    # Only used if 'casing: camel'
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
      prefix: __src_            # Source files start with this prefix
    models:
      prefix: stg_              # Model files start with this prefix
    docs:
      prefix: _stg_             # Docs files start with this prefix
      in_folder: false          # Docs files in separate folder?
      tests:                    # Add generic dbt tests for columns found in schemas
        id: [unique, not_null]

```
</details>

#### `reflekt_profiles.yml`
Defines connection to schema registries and sources where event data is stored.
<details>
<summary><code>example_reflekt_profile.yml</code>(click to expand)</summary>
<br>

```yaml
# Example reflekt_profiles.yml
version: 1.0

dev_reflekt:                                              # Profile name (multiple profiles can be defined)
  registry:                                               # Define connections to schema registries (multiple allowed)
    - type: segment
      api_token: segment_api_token                        # https://docs.segmentapis.com/tag/Getting-Started#section/Get-an-API-token
    - type: avo
      workspace_id: avo_workspace_id                      # https://www.avo.app/docs/public-api/export-tracking-plan#endpoint
      service_account_name: avo_service_account_name      # https://www.avo.app/docs/public-api/authentication#creating-service-accounts
      service_account_secret: avo_service_account_secret

  source:                                                 # Define connections to data warehouses where event data is stored (multiple TYPES allowed. Cannot have sources of the same TYPE)
    - type: snowflake                                     # Snowflake DWH. Credentials follow.
      account: abc12345
      database: raw
      warehouse: transforming
      role: transformer
      user: reflekt_user
      password: reflekt_user_password

    - type: redshift                                      # Redshift DWH. Credentials follow.
      host: example-redshift-cluster-1.abc123.us-west-1.redshift.amazonaws.com
      database: analytics
      port: 5439
      user: reflekt_user
      password: reflekt_user_password

```
</details>

### Metadata
Required metadata can be globally defined for all events in a project by modifying the `metadata` object in the `schemas/.reflekt/event-meta/1-0.json` schema. This is optional and by default no metadata is required.

<details>
<summary><code>schemas/.reflekt/event-meta/1-0.json  (click to expand example)</code></summary>
<br>

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": ".reflekt/event-meta/1-0.json",
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
                        }
                    },
                    "required": ["vendor", "name", "format", "version"],
                    "additionalProperties": false
                },
                "metadata": {  // EXAMPLE: Defining required metadata ( code_owner, product_owner, stakeholders)
                    "type": "object",
                    "description": "Required metadata for all event schemas",
                    "properties": {
                        "code_owner": {
                            "type": "string"
                        },
                        "product_owner": {
                            "type": "string"
                        },
                        "stakeholders": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                    },
                    "required": ["code_owner", "product_owner"],
                    "additionalProperties": false
                },
                "properties": {},
                "tests": {},
                "metrics": {
                    "type": "object",
                    "properties": {
                        "dimensions": {
                            "type": "array",
                            "description": "Schema properties to be used as dimensions",
                            "items": {"type": "string"}
                        },
                        "measures": {
                            "type": "array",
                            "description": "Schema properties to be used as measures",
                            "items": { "type": "string"}
                        }
                    },
                    "required": ["dimensions", "measures"],
                    "additionalProperties": false
                }
            },
            "required": ["self", "metadata", "properties"]
        }
    ]
}

```

</details>


## Schemas
Event schemas stored as JSON files in the `schemas/` directory of a project. Behind the scenes, Reflekt understands how different schema registries store and structure schemas, creating a common codified representation using [JSONschema](https://json-schema.org/). When pulling/pushing schemas from/to a schema registry, Reflekt handles the conversion between the registry's format and JSON Schema.

### Schema `$id`
Schemas are identified in Reflekt by their `$id` property, equal to their relative path to the `schemas/` directory. For example, the schema at `my_reflekt_project/schemas/segment/ecommerce/CartViewed/1-0.json` has the `$id` of `segment/ecommerce/CartViewed/1-0.json`.

See the [--select](#--select) syntax docs for more details on selecting schemas when running commands.

### Schema Versions
Schema changes are captured using a `MAJOR-MINOR` version spec (inspired by [SchemaVer](https://docs.snowplow.io/docs/pipeline-components-and-applications/iglu/common-architecture/schemaver/)). Schema versions start at `1-0` and are incremented as follows:

- **MAJOR** - Breaking schema changes incompatible with previous data. Examples:
  - Add/remove/rename a required property
  - Change a property from *optional to required*
  - Change a property's type
- **MINOR** - Non-breaking schema changes compatible with previous data. Examples:
  - Add/remove/rename an optional property
  - Change a property from *required to optional*

### Schema Registries
Reflekt supports the following schema registries. While Reflekt uses the `MAJOR-MINOR` versioning spec, registries handle schema versions differently. Compatibility with Reflekt's `MAJOR-MINOR` spec is included in the table below.
| Schema Registry   | `MODEL` | `ADDITION` | Notes     |
|-------------------|:-------:|:----------:|:----------|
| Segment Protocols |    ✅    |      ❌    | Only supports `MODEL` (breaking changes).
| Avo               |    ✅    |      ❌    | Schema changes managed in Avo [branches](https://www.avo.app/docs/workspace/branches) - `"version": "1-0"`(always).<br> Avo customers can build data artifacts based on their Avo tracking plan using `reflekt pull` + `reflekt build`. |

### Example schema
An example `ProductClicked` event schema, based on the [Segment Ecommerce Spec](https://segment.com/docs/connections/spec/ecommerce/v2/#product-clicked), is shown below.

<details>
<summary><code>my_reflekt_project/schemas/segment/ecommerce/ProductClicked/1-0.json</code> (click to expand) </summary>
<br>

```json
{
  "$id": "segment/ecommerce/ProductClicked/1-0.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "self": {
      "vendor": "com.company_name",
      "name": "ProductClicked",
      "format": "jsonschema",
      "version": "1-0"
  },
  "metadata": {
      "code_owner": "engineering/ecommerce-squad",
      "product_owner": "product_manager_name@company_name.com",
  },
  "type": "object",
  "properties": {
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
  "required": [],
  "additionalProperties": false,
}
```

</details>


## Using Data Artifacts

### dbt packages
To use a private dbt package built by Reflekt in a downstream dbt project, add it to the `packages.yml` of the project (see examples below) and then run `dbt deps` to import it.

#### dbt-core
```yaml
packages:
  - git: "https://github.com/<your_user_or_org>/<your_repo>"  # Replace with Github repo URL for your Reflekt project
    subdirectory: "dbt-packages/<reflekt_dbt_package_name>"
    revision: v0.1.0___DBT_PKG_NAME_  # Example tag. Replace with branch, tag, or commit (full 40-character hash)
```

#### dbt-cloud
```yaml
packages:
  - git: ""https://{{env_var('DBT_ENV_SECRET_GITHUB_PAT')}}@github.com/<your_user_or_org>/<your_repo>.git""  # Replace with your PAT and Github repo URL for your Reflekt project
    subdirectory: "dbt-packages/<reflekt_dbt_package_name>"
    revision: v0.1.0___DBT_PKG_NAME_  # Example tag. Replace with branch, tag, or commit (full 40-character hash)
```
To use with dbt-cloud, you will need to [create a Github personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) (e.g., `DBT_ENV_SECRET_GITHUB_PAT`) and [configure it as an environment variable](https://docs.getdbt.com/docs/dbt-cloud/using-dbt-cloud/cloud-environment-variables) in your dbt-cloud account.

