<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Install
Install `reflekt` with `pip`. Installing in a virtual Python environment is recommended.
```bash
$ pip install reflekt
```
# Setup

## Demo: Creating a Reflekt project
Gives you a quick sense of how to setup a Reflekt project.

https://user-images.githubusercontent.com/28986302/170632029-d2c06c38-c76d-4d93-9dbb-7c8a842f8792.mp4

## Step-by-step guide
The exact setup steps.
1. Create a git repo or clone one from GitHub.
```bash
# Option 1: Create a Git repo locally
$ mkdir path/to/reflekt-project  # Make a new directory
$ cd path/to/reflekt-project     # Navigate inside directory
$ git init                       # Initialize Git repo

# Option 2: Clone a Git repo from GitHub
$ git clone https://github.com/user/reflekt-project.git
```

2. Initialize a Reflekt project.
```bash
$ cd path/to/reflekt-project
$ reflekt init --project-dir .  # Follow the prompts
```

3. Configure your Reflekt project. See the docs on [Reflekt Projects and Tracking Plans as `code`](TRACKING-PLANS-AS-CODE.md) for guidance on configuration. If you are using Avo, see the [Reflekt + Avo](https://github.com/GClunies/reflekt/blob/main/docs/INSTALL-SETUP.md#reflekt--avo) section below.

4. You are ready to start using Reflekt! See the docs on Reflekt [commands](docs/COMMANDS.md).

### Reflekt + Avo

Configuring Reflekt with [Avo](https://www.avo.app/) requires some additional setup and contacting Avo support (they're super helpful!). But don't worry, you only need to do this once! Here are the steps:

1. Contact Avo support and request access to the JSON source.
2. Install node and node package manager (npm). The [npm docs](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) provide great docs and guidance on this.
3. Install the [Avo CLI](https://www.avo.app/docs/implementation/cli) (requires node & nom) and verify installation.
   ```bash
   $ npm install -g avo
   $ avo --version
     2.0.2
   ```
4. Link and verify your Avo Account using the Avo CLI.
   ```
   $ avo login
   $ avo whoami
     info Logged in as you@somewhere.com
   ```
5. In your Avo account, create a JSON source.
   1. The name you give your JSON source will be used by Reflekt as the plan name. For example: If you set the JSON source name to `your-avo-json-source`, you will pull your tracking plan from Avo by running `reflekt pull --name your-avo-json-source`.
   2. On the JSON source settings page, under the **Avo Functions Setup** tab, set the **Programming Language** to `JSON Schema`.
   3. On the JSON source settings page, click `edit` next to **Events** and select `Send all events in tracking plan`. This will ensure Reflekt searches for all event data in your warehouse when templating your dbt package(s).

6.  Configure Avo with Reflekt
   ```bash
   # From the root of your Reflekt project
   $ cd .reflekt/avo

   $ avo init
     success Initialized for workspace patty-bar
     info Run 'avo pull' to pull analytics wrappers from Avo

   $ avo pull --force
     info Pulling from branch 'main'
     info No sources configured.
     # You will be prompted for the following
     # Replace example values inside < > with your values
     ? Select a source to set up
         # Select the JSON source you created
     ? Select a folder to save the analytics wrapper in
         # Select '.'
     ? Select a filename for the analytics wrapper
         # Type <your-avo-json-source>.json

     success Analytics wrapper successfully updated
     └─ your-avo-json-source
        └─ your-avo-json-source.json
   ```

7. Navigate back to the root of your Reflekt project. Remember, Reflekt **can only be run from the root of a Reflekt project.**
   ```
   $ cd path/to/reflekt/project/root
   ```

8. Configure your Reflekt project. See the docs for details.

9. You are ready! Going forward, you only need to run `reflekt pull --name your-avo-json-source-name` to get the latest version of your tracking plan from Avo.
