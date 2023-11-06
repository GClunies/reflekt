<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt Changelog

## [0.5.0] - 2023-10
### Breaking
- Only support python versions `>=3.9`. Support for pyhton `3.8` is DEPRECATED.


## [0.4.0] - 2023-10
### Added
- `reflekt report` CLI command - create a Markdown formatted report of an event schema. Output to `stdout` or `.md` in same directory as the `.json` file.
- Add common `get_schema_paths()` to `cli.py` so that it can be used by all CLI commands that `--select` schemas.
- Update example schemas in `schemas/segment/ecommerce/`

### Fixed
Use `from __future__ import annotations` so that `from typing import List, Dict, Tuple` is not required in python 3.8.


## [0.3.17] - 2023-03-14
### Fixed
- Handle case where schema author specifies `id` in schema. This is transformed by Segment to `_id` when loading the table in the warehouse. Reflekt now knows to look for a `_id` column when parsing the source table.

## [0.3.16] - 2023-03-07
### Fixed
- Bug in `segment.py` that would caused error when trying to push a single schema to Segment schema registry.

## [0.3.15] - 2023-03-07
### Added
- `reflekt lint` checks for properties that do not have a `type` defined.

## [0.3.14] - 2023-03-07
### Added
- Add `pascal` as a case option for events and properties in event schemas.
### Fixed
- Do not allow spaces in schema paths.
- Removes `capitalize_camel` config from `reflekt_project.yml`
-
## [0.3.13] - 2023-03-07
### Fixed
- Log schema *before* linting, not after.

## [0.3.12] - 2023-03-04
### Added
- Campaign contexts to common Segment schema.

## [0.3.11] - 2023-03-04
### Added
- Device contexts to common Segment schema.

## [0.3.10] - 2023-03-04
### Fixed
- Handle case where `id` in schema properties so it doesn't get aliased to `event_id` (already used by Reflekt).

## [0.3.9] - 2023-03-04
### Fixed
- Fix how duplicated columns are aliased in dbt pkg models.

## [0.3.8] - 2023-03-04
### Fixed
- Fix bug that would add timestamp cols that don't exist in Segment users table.

## [0.3.7] - 2023-03-04
### Fixed
- Fix bug that prevented columns from `identify` schemas being used to model segment users data.
- Ensure page/screen `name` is modelled in dbt regardless of whether they are in the schema `properties`.

## [0.3.6] - 2023-03-03
### Fixed
- Fix to force as alias for duplicated properties when building dbt pkg models.

## [0.3.5] - 2023-03-03
### Fixed
- Fix bug where `_user_id` column was added to models of Segment users data.

## [0.3.4] - 2023-03-03
### Fixed
- Fix bug where `version` column could be duplicated in dbt pkg models for Segment events.

## [0.3.3] - 2023-03-03
### Fixed
- Fix bug where `reflekt build dbt` would fail when building a dbt pkg with Segment `group()` call data.

## [0.3.2] - 2023-02-26
### Added
- Missing docstrings to Reflekt code.
- Anonymous usage stats.

### Changed
- Improve Reflekt project and profile validation.
- Reflekt now stores validation and common schemas internally.
- Update templates for Reflekt projects and dbt packages.
- Update README docs.
- Updated Reflekt meta-schema so that metadata is defined under the `'self'` object.
- Fixed how Avo tags are transformed into Reflekt metadata.


## [0.3.1] - 2023-02-08
### Added
- Added a required filter: config to reflekt_project.yml (can be empty string).

### Changed
- Improves schema checks on reflekt_project.yml and reflekt_profiles.yml.
- Cleanup example schemas and artifacts.
- Fixed templated README when running `reflekt build dbt ...`

## [0.3.0] - 2023-02-06
### Added
- Tests can be run using `tox`.
- Schemas used internally by Reflekt are stored in `schemas/.reflekt/` of a Reflekt project.
- Improved validation of `reflekt_project.yml` and `reflekt_profiles.yml` configuration files using JSON Schema.
- Added `metrics` property to event schemas template in prep for dbt metrics support.
- Simplified docs by moving to [README.md](https://github.com/GClunies/Reflekt/blob/main/README.md)
-  Added this CHANGELOG.

### Changed
- Use [JSON Schema](https://json-schema.org/) instead of YAML to define event schemas.
  - JSON Schema a standard format that is widely used and supported. Better for future integrations.
  - Makes Reflekt code simpler and faster (no converting YAML to JSON behind the scenes).
- Event schemas are now stored in a `schemas/` directory. Previously `tracking-plans/` (schemas may support use cases outside product analytics in the future).
- Required metadata for event schemas is configured in the `schemas/.reflekt/event-meta/1-0.json` meta-schema.
- Replaced `reflekt dbt` with `reflekt build` in prep to support building other data artifact types.
- dbt packages are now built in the `artifacts/dbt/` directory. Previously `dbt-packages/`.
- dbt packages only template staging models as views. Previously, staging models could be incremental, but this was overly complex with little benefit.
- CI suite upgrades.

## <=[0.2.18]
No formal changelog for versions <= 0.2.18, during this time:
- Reflekt used YAML to define event schemas. YAML was thought to be more readable, but user feedback preferred JSON Schema (widely used and supported).
- Lots of *command* configuration was done in `reflekt_project.yml` and `reflekt_profiles.yml`.
