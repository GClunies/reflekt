# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

TITLE_CASE_RE = r"[A-Z][a-z]+"
TITLE_CASE_NUMBERS_RE = r"[A-Z][a-z0-9]+"
CAMEL_CASE_RE = r"(^[a-z]|[A-Z])[a-z]*"
CAMEL_CASE_NUMBERS_RE = r"(^[a-z]|[A-Z0-9])[a-z]*"
SNAKE_CASE_RE = r"^[a-z._]+$"
SNAKE_CASE_NUMBERS_RE = r"^[a-z]*[a-z0-9._]+$"
