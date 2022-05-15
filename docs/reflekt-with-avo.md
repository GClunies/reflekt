<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Using reflekt with Avo
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
