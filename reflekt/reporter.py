# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Union

import jsonschema2md
from loguru import logger


class Reporter:
    """Reflekt Reporter class.

    Generates markdown documentation from a JSON schema file.
    """

    def __init__(self) -> None:
        """Initialize Reflekt Reporter."""
        self.parser = jsonschema2md.Parser()

    def build_md(self, schema_path) -> None:
        logger.info(f"Generating Markdown report for schema in: {schema_path}")

        with open(schema_path, "r") as f:
            schema_obj = json.load(f)

        md_lines = self.parser.parse_schema(schema_obj)
        md_lines[0] = md_lines[0].replace(
            # Reflekt does not use `title` keyword. Replace default with event name.
            # While we're at it, add schema `$id` to report.
            "# JSON Schema",
            f"# {schema_obj['self']['name']}\n`$id`: `{schema_obj['$id']}`",
        )
        md_str = "".join(md_lines)

        return md_str
