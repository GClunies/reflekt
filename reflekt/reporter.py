# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json

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
            # Schemas in Reflekt do not use `title` keyword.
            # Replace default `JSON Schema` value with event name.
            "# JSON Schema",
            f"# {schema_obj['self']['name']}",
        )
        md_lines.insert(  # Add schema `$id` to report
            1, f"`$id`: {schema_obj['$id']}\n\n"
        )
        md_str = "".join(md_lines)

        return md_str
