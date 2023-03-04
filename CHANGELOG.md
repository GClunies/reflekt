<!--
SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>

SPDX-License-Identifier: Apache-2.0
-->

# Reflekt Changelog
## [0.3.7] - 2023-03--03

### Fixes
- Fix bug that prevented columns from `identify` schemas being used to model segment users data.

## [0.3.6] - 2023-03--03

### Fixes
- Fix to force as alias for duplicated properties when building dbt pkg models.

## [0.3.5] - 2023-03--03

### Fixes
- Fix bug where `_user_id` column was added to models of Segment users data.

## [0.3.4] - 2023-03--03

### Fixes
- Fix bug where `version` column could be duplicated in dbt pkg models for Segment events.

## [0.3.3] - 2023-03--03

### Fixes
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
- Adds a required filter: config to reflekt_project.yml (can be empty string).

### Changed
- Improves schema checks on reflekt_project.yml and reflekt_profiles.yml.
- Cleanup example schemas and artifacts.
- Fixes templated README when running `reflekt build dbt ...`

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
