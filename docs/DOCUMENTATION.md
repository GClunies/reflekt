# Reflekt Docs

- [Reflekt Docs](#reflekt-docs)
  - [Install](#install)
  - [Create a Reflekt project](#create-a-reflekt-project)
    - [Connect Reflekt + Segment Protocols](#connect-reflekt--segment-protocols)
    - [Connect Reflekt + Avo](#connect-reflekt--avo)
  - [Project configuration](#project-configuration)
    - [Project structure](#project-structure)
    - [Reflekt project](#reflekt-project)
    - [Reflekt config](#reflekt-config)
  - [Tracking plans as `code`](#tracking-plans-as-code)
    - [Events](#events)
      - [Metadata](#metadata)
      - [Properties](#properties)
    - [Identify traits](#identify-traits)
    - [Group traits](#group-traits)
  - [Commands](#commands)
    - [Command compatibility](#command-compatibility)
    - [`reflekt --help`](#reflekt---help)
    - [`reflekt init`](#reflekt-init)
    - [`reflekt new`](#reflekt-new)
    - [`reflekt pull`](#reflekt-pull)
    - [`reflekt push`](#reflekt-push)
    - [`reflekt test`](#reflekt-test)
    - [`reflekt dbt`](#reflekt-dbt)

## Install
Install Reflekt with `pip`.
```bash
pip install reflekt
```

## Create a Reflekt project

1. Create a Git repo or clone an empty one you've created in GitHub.
```bash
# Option 1: Create a Git repo locally
mkdir path/to/reflekt-project  # Make a new directory
cd path/to/reflekt-project     # Navigate inside directory
git init                       # Initialize Git repo

# Option 2: Clone a Git repo from GitHub
git clone https://github.com/user/reflekt-project.git
```

2. Initialize a new Reflekt project.
```bash
# Navigate inside repo
cd path/to/reflekt-project

# Initialize new Reflekt project and create profile in reflekt_config.yml
reflekt init --project-dir .
```

You've created your first Reflekt project!

### Connect Reflekt + Segment Protocols
I've you've run `reflekt init` as shown in the docs above, you are ready to go!

### Connect Reflekt + Avo
Connecting Reflekt with [Avo](https://www.avo.app/) requires some additional steps. Don't worry, you only need to do this once! Here are the exact steps:

1. Contact Avo using their chat support and request access to the JSON source. They are very responsive!
2. Install Node (recommend using [`nvm`](https://github.com/nvm-sh/nvm)) and Node package manager (`npm`). This follows guidance found in the [npm docs](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
   ```bash
   # Install Node version manager
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
   nvm version  # Outputs Node.js version
   v17.8.0

   # Install Node package manager
   npm install -g npm
   npm -v  # Output npm version
   8.11.0
   ```
3. Install the [Avo CLI](https://www.avo.app/docs/implementation/cli) using `npm`.
   ```bash
   npm install -g avo  # Install Avo CLI
   avo --version       # Verify install
     2.0.2
   ```
4. Link your Avo Account to the Avo CLI.
   ```bash
   avo login   # Link Avo account
   avo whoami  # Verify account link
     info Logged in as you@somewhere.com
   ```
5. In a web browser, login to your Avo account and create a JSON Source. The name of the JSON source will be used by Reflekt as the tracking plan name. In the example below, you would pull your tracking plan from Avo by running `reflekt pull --name my-plan`.

   ![avo-json-source](avo-json-source.png)

6. In the settings for the newly created JSON source:
   1. Click `edit` next to **Events** and select `Send all events in tracking plan`. This ensures Reflekt searches for all event data in your warehouse when templating your dbt package(s).

      ![avo-json-settings-add-events](avo-json-settings-add-events.png)

   2. Under the **Avo Functions Setup** tab, set the **Programming Language** to `JSON Schema`. You don't need to do anything else on this tab.

      ![avo-json-settings-functions](avo-json-settings-functions.png)

7. In your Reflekt project, configure Avo with Reflekt
   ```bash
   # From the root of your Reflekt project
   cd .reflekt/avo

   avo init
     success Initialized for workspace your-avo-workspace-name
     info Run 'avo pull' to pull analytics wrappers from Avo

   avo pull --force
     info Pulling from branch 'main'
     info No sources configured.
     # You will be prompted for the following
     # Replace example values inside < > with your values
     ? Select a source to set up
         # Select the Avo JSON source you created
     ? Select a folder to save the analytics wrapper in
         # Select '.'
     ? Select a filename for the analytics wrapper
         # Type <your-avo-json-source>.json

     success Analytics wrapper successfully updated
     └─ your-avo-json-source
        └─ your-avo-json-source.json
   ```

8. Configure your Reflekt project in the `reflekt_project.yml`. See the [Project configs](https://github.com/GClunies/reflekt/blob/main/docs/DOCUMENTATION.md#project-configs) docs.

## Project configuration

### Project structure
A Reflekt project is a directory of folders and files that define your tracking plans and any templated dbt packages based on those plans.

![reflekt-project-structure](reflekt-project-structure.png)

### Reflekt project
Every Reflekt project has a `reflekt_project.yml`, setting project wide configurations. See the example below to see the available parameters and their descriptions.

```yaml
# Example reflekt_project.yml

# Configurations are REQUIRED unless flagged by an '# OPTIONAL (optional_config:)' comment
# Uncomment OPTIONAL configurations to use them

name: example_project

config_profile: example_profile  # Profile defined in reflekt_config.yml

# OPTIONAL (config_path:)
# config_path: /absolute/path/to/reflekt_config.yml

tracking_plans:
  # For each tracking plan in your Reflekt project, specify the warehouse and
  # schema(s) where Reflekt should search for corresponding event data.
  warehouse:
    database:
      my-plan: raw
    schema:
      # For each tracking plan, specify the schema where raw event data is loaded.
      # When templating dbt packages, Reflekt uses the schema in the dbt package
      # and file names (e.g. reflekt_schema_name__event_name.sql). You can also
      # override the schema by specifying a schema_alias
      # (e.g. reflekt_schema_alias__event_name.sql).
      my-plan:
        - schema: poorly_named_schema
          schema_alias: my_app_web  # OPTIONAL (schema_alias:)

  events:
    naming:        # Naming conventions for events
      case: title  # One of title|snake|camel
      allow_numbers: false
      reserved: []  # Reserved event names (casing matters)

    # OPTIONAL (expected_metadata:)
    # Define a schema for expected event metadata. Tested when running:
    #     reflekt test --name <plan-name>
    expected_metadata:
      code_owner:
        required: true
        type: string
        allowed:
          - Jane
          - John
      stakeholder:
        type: string
        allowed:
          - Product
          - Marketing
          - Sales

  properties:
    naming:        # Naming conventions for properties
      case: snake  # One of title|snake|camel
      allow_numbers: false
      reserved: [] # Reserved property names (casing matters)

    data_types: # Allowed property data types. Available types listed below
      - string
      - integer
      - boolean
      - number
      - object
      - array
      - any
      - 'null'  # Specify null type in quotes

dbt:
  templater:
    sources:
      prefix: _src_reflekt_       # Prefix for templated dbt package sources

    models:
      prefix: reflekt_           # Prefix for models in templated dbt package
      materialized: incremental  # One of view|incremental
      # OPTIONAL (incremental_logic:) [REQUIRED if 'materialized: incremental']
      # Specify the incremental logic to use when templating dbt models.
      # Must include {%- if is_incremental() %} ... {%- endif %} block
      incremental_logic: |
        {%- if is_incremental() %}
        where received_at >= ( select max(received_at_tstamp)::date from {{ this }} )
        {%- endif %}

    docs:
      prefix: _reflekt_           # Prefix for docs in templated dbt package
      in_folder: false            # Write docs in models/docs/ folder?subfolder?

```

### Reflekt config
Similar to dbt's `profiles.yml`, the `reflekt_config.yml` holds profiles used by your Reflekt project to connect and integrate with your Analytics Governance Tool, CDP, and data warehouse. Profiles are configured when you run `reflekt init` to first create your Reflekt project. Two example profiles are provided below.

```yaml
# Example reflekt_config.yml
# Can have more than one profile in reflekt_config.yml
# to support multiple Reflekt projects

# Example One
# CDP = Segment
# Analytics Governance tool = Segment Protocols
# Warehouse = Redshift
example_profile_one:
  plan_type: segment  # Plan in Segment Protocols
  cdp: segment
  workspace_name: <your-workspace>  # From https://app.segment.com/your-workspace/overview
  access_token: <your_token>
  warehouse:
    redshift:
      db_name: <your_database>
      host_url: <your_host_url>  # e.g. xxxx.us-west-1.redshift.amazonaws.com
      port: <your_port>          # e.g. 5439
      user: <your_user>          # Recommend creating a reflekt_user
      password: <your_password>

# Example Two
# CDP = Segment
# Analytics Governance tool = Avo
# Warehouse = Snowflake
example_profile_two:
  cdp: segment
  plan_type: avo
  warehouse:
    snowflake:
      account: <your_account>      # e.g. abc1234
      database: <your_database>    # e.g. raw
      user: <your_user>            # Recommend creating a reflekt_user
      password: <your_password>
      role: <your_role>            # e.g. transformer
      warehouse: <your_warehouse>  # e.g. transforming
```

## Tracking plans as `code`
Tracking plans are managed in a `tracking-plans/` directory of the Reflekt project. Events, identify traits, and group traits all have corresponding YAML files. These YAML files are designed to be ***human-readable*** so that users less comfortable with code can still read and learn to contribute to the code.

![my-plan-example](/docs/my-plan.png)

### Events
Each event in your tracking plan is defined by a YAML file, making it easy to manage and update.

#### Metadata
Event metadata is defined under the `metadata:` config (see example `Product Added` event below). It can be used to tag events with metadata not included when an event fires on your application or servers. Metadata can be whatever you want! Some example use cases are:
- Event `product_owner` (who needs to know if something is wrong)
- Event `code_owner` (who you will fix the code)
- event `priority` (how urgently should we fix an issue?)

Reflekt automatically pulls metadata down from your Analytics Governance tool when running `reflekt pull --name my-plan` using the following logic:
- Segment Protocols -> Event "labels" are converted to `metadata:`
- Avo -> Event "tags" are converted to `metadata:`

#### Properties
Event properties are defined under the `properties:` config (see example `Product Added` event below) down from your Analytics Governance tool when running `reflekt pull`.

```yaml
# Example: product-added.yml
- version: 1
  name: Product Added
  description: Fired when a user adds a product to their cart.
  metadata:  # Event metadata
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

### Identify traits
User traits are defined in a YAML file under a `traits:` config.

```yaml
# identify-traits.yml
traits:
  - name: email
    description: The user's email address.
    type: string
    required: true
  - name: address
    description: The user's mailing address.
    type: string
```
</p></details>

### Group traits
Group traits are defined in a YAML file under a `traits:` config.

```yaml
# group-traits.yml
traits:
  - name: account_name
    description: The account name.
    type: string
    required: true
  - name: is_paying
    description: Does the account pay us?
    type: boolean
```

## Commands

### Command compatibility
Reflekt does not support the `init`, `new`, or `push` commands when connected to Avo. There are two reasons for this:
1. Avo does not support pushing tracking plans back to Avo via the Avo CLI, which Reflekt uses in the background.
2. Since Avo already embraces software engineering workflows (branches, environments) in its web UI, we think it's better for Avo users to manage their tracking plan their and use Reflekt to build dbt packages to model and document the events.

See the table below for command compatibility details.

| Command      | Avo | Segment Protocols |
|--------------|:-----:|:-------------------:|
| reflekt init |  ❌   |         ✅          |
| reflekt new  |  ❌   |         ✅          |
| reflekt pull |  ✅   |         ✅          |
| reflekt push |  ❌   |         ✅          |
| reflekt test |  ✅   |         ✅          |
| reflekt dbt  |  ✅   |         ✅          |


### `reflekt --help`
Show a list of available Reflekt commands.
```bash
reflekt --help
Usage: reflekt [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  dbt   Build dbt package with sources, models, and docs based on...
  init  Create a Reflekt project at the provide directory.
  new   Create a new empty tracking plan using provided name.
  pull  Generate tracking plan as code using the Reflekt schema.
  push  Sync tracking plan to CDP or Analytics Governance tool.
  test  Test tracking plan schema for naming, data types, and metadata.
```

The `--help` flag can also be used with each Reflekt commands. For example:
```bash
reflekt dbt --help
Usage: reflekt dbt [OPTIONS]

  Build dbt package with sources, models, and docs based on tracking plan.

Options:
  --schema TEXT            Schema in which Reflekt will search for raw event
                           data to template.
  --force-version TEXT     Force Reflekt to template the dbt package with a
                           specific semantic version.
  --name TEXT              Tracking plan name in your Reflekt project.
                           [required]
  --help                   Show this message and exit
```


### `reflekt init`
Initialize a new Reflekt project.
```bash
reflekt init --project-dir .  # Create Reflekt project in current folder

Enter your project name (letters, digits, underscore): test_project
...
# Follow the prompts. Creates Reflekt project and reflekt_config.yml
...
11:43:26 Your Reflekt project 'test_project' has been created!

With reflekt, you can:

    reflekt new --name <plan-name>
        Create a new tracking plan, defined as code.

    reflekt pull --name <plan-name>
        Get tracking plan from Analytics Governance tool and convert it to code.

    reflekt push --name <plan-name>
        Sync tracking plan code to Analytics Governance tool. Reflekt handles conversion.

    reflekt test --name <plan-name>
        Test tracking plan code for naming and metadata conventions (defined in reflect_project.yml).

    reflekt dbt --name <plan-name>
        Template dbt package with sources, models, and docs for all events in tracking plan.
```

### `reflekt new`
Create a new tracking plan, defined as code.
```bash
reflekt new --name my-plan
11:58:16 Creating new tracking plan 'my-plan' in '/Users/my_user/path-to/reflekt-project-repo/tracking-plans/my-plan'

11:58:16 [SUCCESS] Created Reflekt tracking plan 'my-plan'
```

### `reflekt pull`
Fetch a tracking plan from Analytics Governance tool.
```bash
reflekt pull --name my-plan
12:20:52 Searching Segment for tracking plan 'my-plan'.
12:20:53 Found tracking plan 'my-plan'
12:20:53 Building Reflekt tracking plan 'my-plan'
12:20:53     Building Reflekt event 'Account Created'
12:20:53     Building Reflekt event 'Account Deleted'
12:20:53     Building Reflekt event 'Checkout Step Viewed'
12:20:53     Building Reflekt event 'Product Added'
12:20:53     Building Reflekt event 'Order Completed'
12:20:53     Building Reflekt event 'Page Viewed'

12:20:53 [SUCCESS] Reflekt tracking plan 'my-plan' built at /Users/gclunies/Repos/reflekt/tracking-plans/my-plan
```

### `reflekt push`
Sync a tracking plan code to an Analytics Governance tool.
```bash
reflekt push --name my-plan
12:32:09 Loading Reflekt tracking plan 'my-plan'
12:32:09     Parsing event file account-created.yml
12:32:11     Parsing event file account-deleted.yml
12:32:12     Parsing event file checkout-step-viewed.yml
12:32:13     Parsing event file product-added.yml
12:32:15     Parsing event file order-completed.yml
12:32:16     Parsing event file page-viewed.yml

12:32:17 Converting Reflekt tracking plan 'tracking-plan-example'to Segment format
12:32:18     Converting 'Account Created'
12:32:18     Converting 'Account Deleted'
12:32:18     Converting 'Checkout Step Viewed'
12:32:18     Converting 'Product Added'
12:32:18     Converting 'Order Completed'
12:32:19     Converting 'Page Viewed'

12:32:20 Syncing converted tracking plan 'tracking-plan-example' to Segment

12:32:21 [SUCCESS] Synced Reflekt tracking plan 'my-plan' to Segment
```

### `reflekt test`
Test tracking plan events, properties, and metadata against rules defined in `reflekt_project.yml`. See the [Reflekt project](#reflekt-project) docs for details on defining naming conventions and expected metadata.
```bash
reflekt push --name my-plan
12:37:36 Loading Reflekt tracking plan 'my-plan'
12:37:36     Parsing event file account-created.yml
12:37:37     Parsing event file account-deleted.yml
12:37:37     Parsing event file checkout-step-viewed.yml
12:37:37     Parsing event file product-added.yml
12:37:39     Parsing event file order-completed.yml
12:37:40     Parsing event file page-viewed.yml

12:38:28 [PASSED] No errors detected in Reflekt tracking plan 'my-plan'
```

### `reflekt dbt`
Template a dbt package modeling and documenting all the events in a tracking plan.
```bash
reflekt dbt --name my-plan

12:47:10 Building Reflekt dbt package:
        cdp: segment
        analytics governance tool: avo
        tracking plan: my-plan
        warehouse: snowflake
        schema: patty_bar_web_staging
        dbt package name: reflekt_patty_bar_web_staging
        dbt package version: 0.1.0
        dbt package path: /Users/gclunies/Repos/reflekt/dbt_packages/reflekt_patty_bar_web_staging

12:46:52 Initializing template for dbt source patty_bar_web_staging

12:46:56 Templating table 'pages' in dbt source patty_bar_web_staging

12:46:56 Templating dbt model reflekt_patty_bar_web_staging__pages.sql
12:46:56     Adding {{ config(...) }} to model SQL
12:46:56     Adding source CTE to model SQL
12:46:56     Adding renamed CTE to model SQL
12:46:56     Adding column 'page_id' to model SQL
12:46:56     Adding column 'source_schema' to model SQL
12:46:56     Adding column 'source_table' to model SQL
12:46:56     Adding column 'tracking_plan' to model SQL
12:46:56     Adding column 'page_name' to model SQL
12:46:56     Adding column 'library_name' to model SQL
12:46:56     Adding column 'library_version' to model SQL
12:46:56     Adding column 'sent_at_tstamp' to model SQL
12:46:56     Adding column 'received_at_tstamp' to model SQL
12:46:56     Adding column 'tstamp' to model SQL
12:46:56     Adding column 'anonymous_id' to model SQL
12:46:56     Adding column 'user_id' to model SQL
12:46:56     Adding column 'page_url_host' to model SQL
12:46:56     Adding column 'referrer_host' to model SQL
12:46:56     Adding column 'ip' to model SQL
12:46:56     Adding column 'user_agent' to model SQL
12:46:56     Adding column 'device' to model SQL
12:46:56     Adding column 'path' to model SQL
12:46:56     Adding column 'product_type' to model SQL
12:46:56     Adding column 'referrer' to model SQL
12:46:56     Adding column 'search' to model SQL
12:46:56     Adding column 'title' to model SQL
12:46:56     Adding column 'url' to model SQL

12:46:56 Templating dbt docs reflekt_patty_bar_web_staging__pages.yml for model reflekt_patty_bar_web_staging__pages.sql
12:46:56     Adding column 'page_id' to dbt docs
12:46:56     Adding column 'source_schema' to dbt docs
12:46:56     Adding column 'source_table' to dbt docs
12:46:56     Adding column 'tracking_plan' to dbt docs
12:46:56     Adding column 'page_name' to dbt docs
12:46:56     Adding column 'library_name' to dbt docs
12:46:56     Adding column 'library_version' to dbt docs
12:46:56     Adding column 'sent_at_tstamp' to dbt docs
12:46:56     Adding column 'received_at_tstamp' to dbt docs
12:46:56     Adding column 'tstamp' to dbt docs
12:46:56     Adding column 'anonymous_id' to dbt docs
12:46:56     Adding column 'user_id' to dbt docs
12:46:56     Adding column 'page_url_host' to dbt docs
12:46:56     Adding column 'referrer_host' to dbt docs
12:46:56     Adding column 'ip' to dbt docs
12:46:56     Adding column 'user_agent' to dbt docs
12:46:56     Adding column 'device' to dbt docs
12:46:56     Adding column 'path' to docs
12:46:56     Adding column 'product_type' to docs
12:46:56     Adding column 'referrer' to docs
12:46:56     Adding column 'search' to docs
12:46:56     Adding column 'title' to docs
12:46:56     Adding column 'url' to docs

...
...
...
# More output to stdout for each model
...
...
...

12:47:23 [SUCCESS] Created Reflekt dbt package 'reflekt_patty_bar_web_staging' at: /Users/gclunies/Repos/reflekt/dbt_packages/reflekt_patty_bar_web_staging

Would you like to create a Git tag to easily reference Reflekt dbt package reflekt_patty_bar_web_staging (version: 0.1.0) in your dbt project? [y/N]: N
```
