# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path
from typing import List

from loguru import logger

from reflekt.builder.dbt import DbtBuilder
from reflekt.profile import Profile
from reflekt.project import Project


class BuilderHandler:
    """Handler to initialize a builder based on artifact, select, and source arguments.

    Handler passes the schemas to be built to the builder.
    """

    def __init__(
        self,
        artifact_arg: str,
        select_arg: str,
        sdk_arg: str,
        source_arg: str,
        profile: Profile,
    ) -> None:
        """Initialize BuilderHandler class.

        Args:
            artifact_arg (str): The --artifact argument passed to Reflekt CLI.
            select_arg (str): The --select argument passed to Reflekt CLI.
            sdk_arg (str): The --sdk argument passed to Reflekt CLI.
            source_arg (str): The --source argument passed to Reflekt CLI.
            profile (Profile): Reflekt Profile object.
        """
        self.select_arg = select_arg
        self.artifact_arg = self._parse_artifact(artifact_arg)
        self.schema_paths = self._parse_select(select_arg)
        self.sdk_arg = sdk_arg
        self.source_arg = source_arg
        self.profile = profile

    def _parse_artifact(self, artifact: str) -> None:
        """Parse the artifact argument.

        Args:
            artifact (str): The --artifact argument passed to Reflekt CLI.

        Raises:
            NotImplementedError: If artifact is not supported.

        Returns:
            str: Artifact type.
        """
        if artifact not in ["dbt"]:
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

        if self.artifact_arg == "dbt":
            builder = DbtBuilder(
                select_arg=self.select_arg,
                schema_paths=self.schema_paths,
                sdk_arg=self.sdk_arg,
                source_arg=self.source_arg,
                profile=self.profile,
            )

        return builder
