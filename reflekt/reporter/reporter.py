# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path

from loguru import logger

from reflekt.reporter.jsonschema2md import JSONParser


class Reporter:
    """Reflekt Reporter class.

    Generates markdown documentation from a JSON schema file.
    """

    def __init__(self) -> None:
        """Initialize Reflekt Reporter."""
        self.parser = JSONParser()

    def build_md(self, schema_path: Path) -> str:
        """Build a markdown report from a JSON schema file.

        Args:
            schema_path (Path): Path to JSON schema file.

        Returns:
            str: Markdown report string for the schema.
        """
        logger.info(f"Generating Markdown report for schema in: {schema_path}")

        with open(schema_path, "r") as f:
            schema_obj = json.load(f)

        md_lines = self.parser.parse_schema(schema_obj)
        md_str = "".join(md_lines)

        return md_str
