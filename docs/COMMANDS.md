# Commands
1. Create a Reflekt project.
   ```bash
   $ reflekt init --project-dir ./my_reflekt_project  # Follow the prompts
   ```

2. Get a tracking plan from your Analytics Governance Tool (Segment Protocols, Avo, others coming soon) and convert it to a Reflekt tracking plan code, ready for templating.
   ```bash
   $ reflekt pull --name <plan-name>
   ```

3. Use the Reflekt dbt templater to save your data team time. Stop manually writing dbt source, models, and documentation for your event data.
   ```bash
   $ reflekt dbt --name <plan-name>
   ```
   As your tracking plan changes, re-template to capture updates/changes. Reflekt will bump the version of your dbt package as it evolves with your tracking plan.

4. Sync your Reflekt tracking plan to your Analytics Governance tool (Segment Protocols, others coming soon). Reflekt handles the conversion!
   ```bash
   $ reflekt push --name <plan-name>
   ```

5. Test events and properties in your tracking plan for naming conventions, data types, and expected metadata.
   ```zsh
   $ reflekt test --name <plan-name>
   ```

6. Create a new tracking plan, defined as code.
   ```bash
   $ reflekt new --name <plan-name>
   ```
