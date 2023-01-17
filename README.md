<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt

A CLI tool to help Data, Engineering, and Product teams:
- Define event schemas as `code` using [JSON Schema](https://json-schema.org/), providing a version controlled source of truth for events.
- Lint schemas to enforce agreed-upon conventions (configurable). Run `reflekt lint` in a CI/CD pipeline to check:
    - Naming conventions (snake_case, camelCase, Title Case, etc.)
    - Descriptions are always included.
    - Required metadata is defined.
- Interact with schema registries
  - Sync schema(s) to a schema registry where they can be used for event data validation.
  - Pull schema(s) from a schema registry to into a Reflekt project.
- Leverage schemas to build data artifacts (e.g., dbt packages) that model and document event data.
  - Keep data artifacts in sync with instrumentation - Ready for use by engineers, analysts, and the business.
  - Reduce errors, improve data quality, and automate important (but boring) data tasks.

---

## Commands
A full list of commands and their arguments can be accessed in the CLI using `reflekt --help`. Each command has a `--help` flag with information about the command and its arguments/options.
 See the [argument syntax](#argument-syntax) section for more information on how to use arguments and the [schemas](artifacts/dbt/reflekt_demo/dbt_project.yml) section for more information on how schemas are identified, version, and structured.

### `init`
Initialize a new Reflekt project.
```bash
reflekt init --dir /path/to/project
```

### `pull`
Pull schemas from a schema registry and create the corresponding structure in project `schemas/` directory.
```bash
# Pull all versions of CartViewed schema from Segment to schemas/segment/ecommerce/CartViewed/
reflekt pull --select segment/ecommerce/CartViewed
```

### `push`
Push schemas in project `schemas/` directory to a schema registry.
```bash
# Push all schemas in schemas/segment/ecommerce/ to Segment tracking plan 'ecommerce'
reflekt push -s segment/ecommerce/CartViewed
```

### `lint`
Lint schemas in project `schemas/` directory.
```bash
# Lint a single schema (.json is optional)
reflekt lint -s segment/ecommerce/CartViewed/1-0.json
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
#   - Raw event data stored at specified target (snowflake.raw.segment_prod)
reflekt build dbt --select segment/ecommerce --target snowflake.raw.segment_prod --sdk segment
```

Currently supported artifacts:
- [dbt packages](https://docs.getdbt.com/docs/build/packages) - defines sources, models, and documentation for event data found in specified [target](#targets).


## Argument syntax

### --select
The `--select` / `-s` argument specifies what schema(s) a [command](#commands) is run against using their [schema `$id`](#schema-id). Schemas can be selected from:
1. Schema registries (e.g., Segment, Avo, etc.)
   ```bash
   # Pull schemas from 'ecommerce' tracking plan in Segment registry to my_reflekt_project/schemas/segment/ecommerce/
   reflekt pull -s segment/ecommerce
   ```

2. JSON files in the `schemas/` directory of a Reflekt project.
   ```bash
   # Push my_reflekt_project/schemas/segment/ecommerce/CartViewed/1-0.json to 'ecommerce' tracking plan in Segment registry
   reflekt push -s segment/ecommerce/CartViewed/1-0.json
   ```

More examples of the `--select` syntax are shown in the [commands](#commands) section.

### --target
The `--target` / `-t` argument specifies where Reflekt should search for event data when building data artifacts (e.g., dbt packages). The `--target` argument always follows the `target_name.database_name.schema_name` format. Targets are defined in the [reflekt_profile.yml](#reflekt_profileyml) file.

### --sdk
Different teams use different SDKs to collect event data. When [building a data artifact](#build), the `--sdk` / `-sdk` argument tells Reflekt how the data is structured in the [target](#--target) so that it can build the data artifact accordingly. Currently supported SDKs include:
- [`segment`](https://segment.com/)

---

## Schemas
Event schemas are stored as `.json` files in the `schemas/` directory. Reflekt understands how different schema registries store and structure schemas, creating a codified representation using [JSON Schema](https://json-schema.org/). When pulling/pushing schemas from/to a schema registry, Reflekt handles the conversion between the registry's format and JSON Schema.

### Schema `$id`
Reflekt uses the JSON schema `$id` property to identify schemas, determined by their path relative to the `schemas/` directory. For example, the schema at `my_reflekt_project/schemas/segment/ecommerce/CartViewed/1-0.json` has the `$id` `segment/ecommerce/CartViewed/1-0.json`.

See the [--select](#--select) syntax docs for more details on selecting schemas when running commands.

### Schema version
Schema changes are captured using a `MAJOR-MINOR` version spec (inspired by [SchemaVer](https://docs.snowplow.io/docs/pipeline-components-and-applications/iglu/common-architecture/schemaver/)). Schema versions start at `1-0` and are incremented as follows:

- **MAJOR** - Breaking schema change that is incompatible with previous data. Examples:
  - Add/remove/rename a required property
  - Change a property from *optional to required*
  - Change a property's type
- **MINOR** - Non-breaking schema change that is compatible with previous data. Examples:
  - Add/remove/rename an optional property
  - Change a property from *required to optional*

### Schema registries
Reflekt supports the following schema registries. While Reflekt uses the `MAJOR-MINOR` versioning spec, each registry handles schema versions differently. Compatibility with Reflekt's `MAJOR-MINOR` spec is included in the table below.
| Schema Registry   | `MODEL` | `ADDITION` | Notes     |
|-------------------|:-------:|:----------:|:----------|
| Segment Protocols |    ✅    |      ❌    | Only supports `MODEL` (breaking changes).
| Avo               |    ✅    |      ❌    | Schema changes managed in Avo [branches](https://www.avo.app/docs/workspace/branches) - `"version": "1-0"`(always).<br> Avo customers can build data artifacts based on their Avo tracking plan using `reflekt pull` + `reflekt build`. |

### Example schema
An example `ProductClicked` event schema, based on Segment's [Ecommerce Spec](https://segment.com/docs/connections/spec/ecommerce/v2/#product-clicked), is shown below.

<details>
<summary><code>my_reflekt_project/schemas/segment/ecommerce/ProductClicked/1-0.json</code> (CLICK TO EXPAND) </summary>
<br>

```json
{
  "$id": "segment/ecommerce/ProductClicked/1-0.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "self": {
      "vendor": "com.my_company",
      "name": "ProductClicked",
      "format": "jsonschema",
      "version": "1-0"
  },
  "metadata": {
      "code_owner": "engineering/ecommerce-squad",
      "product_owner": "product_manager_name@my_company.com",
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
  "metrics": {
      "dimensions": [],
      "measures": []
  }
}
```

</details>

---

## Project Configuration

Reflekt is configured using the following files. Click the examples below to expand and see example configurations with descriptions.

<details>
<summary><code>reflekt_project.yml</code> - general project settings, linting config, data artifacts config. </summary>
<br>

```yaml
# GENERAL CONFIG ----------------------------------------------------------------------
version: 1.0

name: reflekt_demo      # Project name
vendor: com.my_company  # Default vendor for schemas in reflekt project
profile: dev_reflekt    # Profile to use from reflekt_profiles.yml
# profiles_path: path/to/reflekt_profiles.yml  # Optional. Default: ~/.reflekt/reflekt_profiles.yml

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
    data_types: [string, integer, number, boolean, object, array, any, 'null']

# REGISTRY CONFIG ---------------------------------------------------------------------
registry:                 # Additional config for schema registries (i.e. branch IDs)
  avo:
    branches:
      staging: HqC13KbRJ  # Branch ID for staging tracking plan. Safe to version control. Used by `reflekt pull`
      main: main

# ARTIFACTS CONFIG -----------------------------------------------------------------------
artifacts:              # Configure how data artifacts are built
  dbt:                  # dbt package config
    sources:
      prefix: __src_    # Source files start with this prefix
    models:
      prefix: stg_      # Model files start with this prefix
    docs:
      prefix: _stg_     # Docs files start with this prefix
      in_folder: false  # Docs files in separate folder?
      tests:            # Add tests for specific columns
        id: [unique, not_null]

```

</details>
<br>

<details>
<summary><code>reflekt_profile.yml</code> - connection to schema registries. Connection to targets (i.e., data warehouse) where event data is stored. </summary>
<br>

```yaml
version: 1.0
dev_reflekt:
  registry:
    - type: segment
      api_token: segment_api_token                        # https://docs.segmentapis.com/tag/Getting-Started#section/Get-an-API-token
    - type: avo
      workspace_id: avo_workspace_id                      # https://www.avo.app/docs/public-api/export-tracking-plan#endpoint
      service_account_name: avo_service_account_name      # https://www.avo.app/docs/public-api/authentication#creating-service-accounts
      service_account_secret: avo_service_account_secret
  target:              # Define target(s) (i.e., data warehouses) where event data is stored
    - name: snowflake  # Target name used in --target target_name.database_name.schema_name argument. Does not have to match `type:` config
      type: snowflake  # Snowflake data warehouse. Credentials follow.
      account: yta05625
      database: raw
      warehouse: transforming
      role: transformer
      user: reflekt_user
      password: reflekt_user_password

    - name: redshift
      type: redshift   # Redshift data warehouse. Credentials follow.
      host: example-redshift-cluster-1.abc123.us-west-1.redshift.amazonaws.com
      database: raw
      port: 5439
      user: reflekt_user
      password: reflekt_user_password

```

</details>
<br>

<details>
<summary><code>schemas/.reflekt/event-meta/1-0.json</code> - OPTIONAL: modify `metadata` schema to required specific metadata for all events. Default: no metadata.</summary>
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


