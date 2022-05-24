<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt
Reflekt is a command line tool that connects to your analytics governance tool (e.g. [Segment Protocols](https://segment.com/docs/protocols/), [Avo](https://www.avo.app/)) and defines your tracking plans as `code`. Reflekt uses this code to template **dbt packages modeling and documenting all the events in your tracking plan**, including:
- dbt [sources](https://docs.getdbt.com/docs/building-a-dbt-project/using-sources) pointing to the schema and tables in your warehouse storing the raw event data.
- dbt [models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models) for each event in your tracking plan. Light transformations make your event data ready for consumption or further modeling.
- dbt [documentation](https://docs.getdbt.com/docs/building-a-dbt-project/documentation) for every model in the package, pulling information directly from the tracking plan. Your data team and the business always know what your tables and columns mean.

Reflekt integrates with your analytics governance tool (e.g. [Segment Protocols](https://segment.com/docs/protocols/), [Avo](https://www.avo.app/)), customer data platform (e.g. [Segment](https://segment.com/)), data warehouse, and [dbt](https://www.getdbt.com/).

![reflekt-arch](/docs/reflekt_architecture.png)

Reflekt can also be used to manage tracking plans:
- Pull tracking plans from your analytics governance tools, converting them to code.
- Push changes to your tracking plan code back to your analytics governance tools, Reflekt handles the conversion.
- Create new tracking plans defined as code.
- Test tracking plan code for naming conventions and required metadata. You define the rules in your `reflekt_project.yml`.
- Makes your tracking plan an *extensible* artifact that you can build off of, similar to dbt's `manifest.json`.

## Getting started
- [Install & Setup](docs/INSTALL-SETUP.md)
- [Reflekt Projects and Tracking Plans as `code`](docs/TRACKING-PLANS-AS-CODE.md)
- [Commands](docs/COMMANDS.md)

https://user-images.githubusercontent.com/28986302/169673197-f5ae1d60-682d-4c85-ad82-4f7fb31be128.mp4

## FAQ
**Q:** **Do I have to use Reflekt to manage my tracking plan(s)? What if I like my analytics governance tool and just want to use the dbt templater?**

**A:** Reflekt lets you decide what features you want to use. Here are two examples:
1. Manage your tracking plan in Avo, pull the plan from Avo into your Reflekt Project, and template your dbt packages using `reflekt dbt --name my-plan`. Pull plan changes from Avo and template again as needed.
2. Manage your tracking plan(s) as code in a Reflekt project, sync changes to Segment Protocols with `reflekt push --name my-plan` so the plan can be used for event validation. Now you can develop your tracking plan code the same way your software engineers develop applications - using pull requests, branches, environments, testing, and CI.

**Q:** **If the tracking plan is `code`, how can a product manager, marketer, etc. propose changes?**

**A:** This question assumes code is only for engineers - we strongly disagree! *Anyone* can learn how Reflekt defines tracking plans as code, which is why the code is designed to be *human-readable*. In Reflekt, tracking plans are defined in a `tracking-plans/` folder with each event defined using a simple YAML file.

<details><summary><strong>example-event.yml</strong> (click to expand)</summary><p>

```yaml
# Example 'Product Added' event
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

![my-plan-example](docs/my-plan-example.png)

With this simple structure and file format, anyone can be taught to make changes to the tracking code and submit a PR using GitHub's web interface. No terminal or IDE required!

**Q:** **What analytics governance tools does Reflekt support?**

**A:** Reflekt currently supports [Segment Protocols](https://segment.com/docs/protocols/) and [Avo](https://www.avo.app/).

**Q:** **What customer data platforms (CDPs) does Reflekt support?**

**A:** Reflekt currently supports data collected using [Segment](https://segment.com/). Support for [Rudderstack](https://www.rudderstack.com/) is being investigated.

**Q:** **What data warehouses does Reflekt support?**

**A:** Reflekt currently works with [Snowflake](https://www.snowflake.com/) and [Redshift](https://aws.amazon.com/redshift/).

## Beliefs
The core belief of Reflekt is **the tracking plan is the most important artifact in a product analytics stack.** Without one, product and data teams can easily find themselves lost. How the tracking code is instrumented, event validation, raw data, transformed data, documentation, and the insights from you analysis - are all dependent on the tracking plan. Tracking plans should be:
- Able to be represented as `code`. This does not prevent the use of SaaS analytics governance tools. These tools should work in unison.
- Version controlled, with branches and environments for different development stages (i.e. dev/staging/prod).
- Extensible (e.g. Reflekt's dbt templater), powering integrations with other tools in the stack.
- Support user-defined metadata (e.g. a "code owner" for each event).
- Leverage continuous integration to test and deploy changes to plans, events, and properties.

In addition to the beliefs above, Reflekt is betting on the following trends in the product analytics space:
- More explicit tracking. Less implicit tracking.
- Product analytics increasingly powered by the data warehouse and dbt.
- dbt [metrics](https://docs.getdbt.com/docs/building-a-dbt-project/metrics) / [metrics layer](https://docs.getdbt.com/docs/dbt-cloud/using-dbt-cloud/cloud-metrics-layer) - imagine defining metrics in the tracking plan and Reflekt templating them in dbt for you. 📈

## Reporting bugs
If you want to report a bug or request a feature, please open an [issue](https://github.com/GClunies/reflekt/issues).

## Contributing code
Feel free to open a [Pull Request](https://github.com/GClunies/reflekt/pulls) for contributions you would like to propose. See the [contributing](docs/CONTRIBUTING-CODE.md) docs for development environment details and guidance.
