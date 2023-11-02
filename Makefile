# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

.PHONY: format
format:
	@ruff format ./reflekt ./tests
	@ruff check --fix ./reflekt ./tests

.PHONY: lint
lint:
	@ruff check ./reflekt ./tests

.PHONY: type-check
type-check:
	@mypy .
