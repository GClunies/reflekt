<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt Commands
1. Create a Reflekt project.
   ```bash
   $ reflekt init --project-dir ./my_reflekt_project  # Follow the prompts
   ```

2. Get a tracking plan from your Analytics Governance Tool (Segment Protocols, Avo, others coming soon) and convert it to a Reflekt tracking plan code, ready for templating.
   ```bash
   $ reflekt pull --name <plan-name>
   ```

3. Use the Reflekt dbt templater to save your data team time. As your tracking plan changes, re-template to model the changes. Reflekt will bump the version of your dbt package as it evolves with your tracking plan.
   ```bash
   $ reflekt dbt --name <plan-name>
   ```

4. Sync your Reflekt tracking plan to your Analytics Governance tool. Reflekt handles the conversion!
   ```bash
   $ reflekt push --name <plan-name>
   ```
   **NOTE** - `reflekt push` does not support Avo. If you use Avo, we recommend managing your plan there and using `reflekt pull` and `reflekt dbt` to pull your plans and template your dbt models as needed.

5. Test events and properties in your tracking plan for naming conventions, data types, and expected metadata.
   ```zsh
   $ reflekt test --name <plan-name>
   ```

6. Create a new tracking plan, defined as code.
   ```bash
   $ reflekt new --name <plan-name>
   ```
