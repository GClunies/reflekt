<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

## Install
Install `reflekt` with `pip`. Recommend installing in a virtual Python environment.
```bash
$ pip install reflekt
```

## Setup
Create a Reflekt project.
```bash
$ reflekt init --project-dir ./my_reflekt_project  # Follow the prompts
$ cd my_reflekt_project                            # Navigate inside project
```

Your Reflekt project includes an example tracking plan in the `tracking-plans/` folder. See the list of commands to learn how to convert the tracking plan in your Analytics Governance tool to code, ready for templating.

#### reflekt with Avo
Using Reflekt with Avo is an experimental feature. It requires additional setup and configuration - see these docs on [using reflekt with Avo](docs/reflekt-with-avo.md).
