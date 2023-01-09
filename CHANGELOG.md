<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
SPDX-License-Identifier: Apache-2.0
-->

# Reflekt Changelog

## [Unreleased]

## [0.3.0] - 2023-01-08

### Added
- Tests run using `tox`.
- Schemas used internally by Reflekt are stored in `schemas/.reflekt/` of Reflekt project.
- Improved validation of `reflekt_project.yml` and `reflekt_profiles.yml` configuration files using JSON Schema.
- Added `metrics` property to event schemas template in prep for dbt metrics support.

### Changed
- Reflekt uses [JSON Schema](https://json-schema.org/) instead of YAML to define event schemas.
  - This a standard format that is widely used and supported. Better for future integrations.
  - Makes Reflekt code simpler and faster (no converting YAML to JSON behind the scenes).
- Event schemas are now stored in a `schemas/` directory. Previously `tracking-plans/` (schemas may support use cases outside product analytics in the future).
- Required metadata for event schemas is configured in the `schemas/.reflekt/event-meta/1-0.json` meta-schema.
- Replaced `reflekt dbt` with `reflekt build` in prep to support building other data artifact types.
- dbt packages are now built in a `artifacts/dbt/` directory. Previously `dbt-packages/`.
- dbt packages only template staging models as views. Previously, staging models could be incremental, but this was overly complex with little benefit.

## <=[0.2.18]
No formal changelog for versions <= 0.2.18, during this time:
- Reflekt used YAML to define event schemas. YAML was thought to be more readable, but user feedback preferred JSON Schema (widely used and supported).
- Lots of *command* configuration was done in `reflekt_project.yml` and `reflekt_profiles.yml`.
