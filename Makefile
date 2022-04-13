# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

.PHONY: format
format:
	@autoflake --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports --recursive --in-place .
	@isort -rc .
	@black .

.PHONY: lint
lint:
	@flake8 .
	@black --check .

.PHONY: type-check
type-check:
	@mypy .
