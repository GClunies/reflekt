# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

.PHONY: format
format:
	@autoflake --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports --recursive --in-place .
	@isort .
	@black .

.PHONY: lint
lint:
	@flake8 ./reflekt ./tests
	@black --check .

.PHONY: type-check
type-check:
	@mypy .
