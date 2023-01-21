# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path
from typing import List

import yaml
from jsonschema import validate
from loguru import logger

from reflekt.dumper import ReflektYamlDumper
from reflekt.project import Project


PROFILE_VERSION = 1.0


class Profile:
    """
    Profile class.

    Describes a Reflekt profile and its configuration from reflekt_profiles.yml.
    """

    def __init__(self, project: Project) -> None:
        """Initialize a Reflekt profile.

        Args:
            project (Project): A Reflekt project class object.

        Raises:
            SystemExit: An error occurred while initializing the project.
        """
        self.project: Project = project
        self.path: Path = project.profiles_path
        self.name: str = project.profile
        self.version: float = 1.0
        self.exists: bool = False
        self.config: dict = {}
        self.do_not_track = False
        self.registry: List = []
        self.source: List = []

        if self.project.exists:  # False when running 'reflekt init'
            if not self.path.exists():
                logger.error(
                    f"'profiles_path: {self.project.profiles_path}' specified in "
                    f"{self.project.path} does not exist"
                )
                raise SystemExit(1)

            with self.path.open() as f:
                profiles = yaml.safe_load(f)

            try:
                self.config = profiles[self.name]
            except KeyError:
                logger.error(f"Profile '{self.name}' not found in {self.path}")
                raise SystemExit(1)

            self.validate_profile()

            self.do_not_track = self.config.get("do_not_track")
            self.registry = self.config.get("registry")
            self.source = self.config.get("source")

    def to_yaml(self):
        """Convert Profile class to YAML and write to reflekt_profiles.yml."""
        if self.path.exists():
            with self.path.open() as f:
                profiles = yaml.safe_load(f)

            profile = {
                self.name: {
                    "registry": self.registry,
                    "source": self.source,
                },
            }
            profiles.update(profile)

        else:
            profiles = {
                "version": self.version,
                self.name: {
                    "registry": self.registry,
                    "source": self.source,
                },
            }

        with self.path.open("w") as f:
            yaml.dump(
                profiles,
                f,
                indent=2,
                width=70,
                Dumper=ReflektYamlDumper,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
                encoding=("utf-8"),
            )

    def validate_profile(self):
        """Validate Reflekt profile configuration."""
        schema_path = self.project.dir / "schemas/.reflekt/profile/1-0.json"

        with schema_path.open() as f:
            schema = json.load(f)

        validate(self.config, schema)


if __name__ == "__main__":  # pragma: no cover
    project = Project()
    profile = Profile(project=project)
    profile.validate_profile()
