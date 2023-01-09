# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path
from typing import List

from loguru import logger

from reflekt.builder.dbt import DbtBuilder
from reflekt.project import Project


class BuilderHandler:
    """Handler to initialize a builder based on artifact, select, and target arguments.

    Handler passes the schemas to be built to the builder.
    """

    def __init__(self, artifact: str, select: str, sdk: str, target: str) -> None:
        """Initialize BuilderHandler class.

        Args:
            artifact (str): The --artifact argument passed to Reflekt CLI.
            select (str): The --select argument passed to Reflekt CLI.
            sdk (str): The --sdk argument passed to Reflekt CLI.
            target (str): The --target argument passed to Reflekt CLI.
        """
        self.select = select
        self.artifact = self._parse_artifact(artifact)
        self.schema_paths = self._parse_select(select)
        self.sdk = sdk
        self.target = target

    def _parse_artifact(self, artifact: str) -> None:
        """Parse the artifact argument.

        Args:
            artifact (str): The --artifact argument passed to Reflekt CLI.

        Raises:
            NotImplementedError: If artifact is not supported.

        Returns:
            str: Artifact type.
        """
        if artifact not in ["dbt"]:  # TODO - add to this list as needed
            raise NotImplementedError(f"Artifact type '{artifact}' is not supported.")
        else:
            return artifact

    def _parse_select(self, select: str) -> List[Path]:
        """Parse the select argument.

        Args:
            select (str): The --select argument passed to Reflekt CLI.

        Returns:
            List[Path]: List of schemas to build.
        """
        schema_paths = []  # List of schema paths to pull
        project = Project()
        select_path = project.dir / "schemas" / select
        logger.info(f"Searching for JSON schemas in: {str(select_path)}")
        print("")

        if select_path.is_dir():  # Get all schemas in directory
            for root, _, files in os.walk(select_path):
                for file in files:
                    if file.endswith(".json"):
                        schema_paths.append(Path(root) / file)
        else:  # Get single schema file
            if select_path.exists():
                schema_paths.append(select_path)

        logger.info(f"Found {len(schema_paths)} schemas to build")

        return schema_paths

    def get_builder(self) -> DbtBuilder:
        """Get builder class based on specified artifact type.

        Returns:
            DbtBuilder: Builder class for specified artifact type.
        """

        if self.artifact == "dbt":
            builder = DbtBuilder(
                select=self.select,
                schema_paths=self.schema_paths,
                sdk=self.sdk,
                target=self.target,
            )

        return builder
