# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import os
import pkgutil
from pathlib import Path
from typing import List, Optional

import yaml
from jsonschema import ValidationError, validate

from reflekt.dumper import ReflektYamlDumper
from reflekt.project import Project


PROFILE_VERSION = 1.0


class Profile:
    """
    Profile class.

    Describes a Reflekt profile and its configuration from reflekt_profiles.yml.
    """

    def __init__(
        self,
        project: Project,
        profile_name: Optional[str] = None,
        from_reflekt_init: bool = False,
    ) -> None:
        """Initialize a Reflekt profile.

        Args:
            project (Project): A Reflekt project class object.
            profile_name (Optional[str]): Name of profile to initialize. If None,
                initialize default_profile in reflekt_project.yml.
            from_reflekt_init (bool): Whether or not the profile is being initialized
                from the 'reflekt init' command. Defaults to False.

        Raises:
            ProfileError: An error occurred while initializing the profile.
        """
        self.project: Project = project
        self.path: Path = project.profiles_path

        if not self.path.exists():
            raise ProfileError(
                message=(
                    f"Profile path '{self.path}' specified in "
                    f"{self.project.path} does not exist"
                ),
                profile=self,
            )

        self.dir = self.path.parent

        if profile_name is not None:
            self.name: str = profile_name
        else:
            self.name: str = project.default_profile

        self.version: float = 1.0
        self.exists: bool = False
        self.config: dict = {}
        self.do_not_track = False
        self.registry: List = []
        self.source: List = []

        if self.project.exists:  # False when running 'reflekt init'
            if (
                not from_reflekt_init
            ):  # Only validate profile if not running 'reflekt init'
                if not self.path.exists():
                    error_msg = (
                        f"'profiles_path: {self.project.profiles_path}' specified in "
                        f"{self.project.path} does not exist"
                    )
                    raise ProfileError(error_msg, profile=self)

                with self.path.open() as f:
                    profiles = yaml.safe_load(f)

                try:
                    self.config = profiles[self.name]
                except KeyError:
                    error_msg = f"Profile '{self.name}' not found in {self.path}"
                    raise ProfileError(error_msg, profile=self)

                try:
                    self.validate_profile()
                except ValidationError as e:
                    raise ProfileError(
                        message=(
                            f"Invalid reflekt_profile.yml: {e.message} at "
                            f"'{e.json_path.replace('$.', '')}'. See the docs at "
                            f"https://github.com/GClunies/Reflekt#reflekt_profilesyml "
                            f"for details on project configuration."
                        ),
                        project=self,
                    )

                self.do_not_track = self.config.get("do_not_track")
                self.registry = self.config.get("registry")
                self.source = self.config.get("source")

                self._check_unique_source_ids()

    def to_yaml(self):
        """Convert Profile class to YAML and write to reflekt_profiles.yml."""
        if self.path.exists():
            with self.path.open() as f:
                profiles = yaml.safe_load(f)

            if self.do_not_track:
                profile = {
                    self.name: {
                        "do_not_track": self.do_not_track,
                        "registry": self.registry,
                        "source": self.source,
                    },
                }
            else:
                profile = {
                    self.name: {
                        "registry": self.registry,
                        "source": self.source,
                    },
                }

            profiles.update(profile)  # Add profile to profiles dict

        else:
            profiles = {
                "version": self.version,
                self.name: {
                    "registry": self.registry,
                    "source": self.source,
                },
            }

        # Check that that profile directory exists
        if not self.dir.exists():
            os.makedirs(self.dir)

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

    def _check_unique_source_ids(self):
        """Check that source IDs are unique.

        Raises:
            ProfileError: Source IDs found in Profile are not unique.
        """
        source_ids = [source["id"] for source in self.source]
        if len(source_ids) != len(set(source_ids)):
            error_msg = (
                f"Duplicate source 'id' in profile: '{self.name}' in {self.path}. "
                f"\n\n    Duplicated source ids: "
                f"{[x for x in source_ids if source_ids.count(x) > 1]}\n"
            )
            raise ProfileError(error_msg, profile=self)

    def validate_profile(self):
        """Validate Reflekt profile configuration."""
        schema = json.loads(pkgutil.get_data("reflekt", "_validation/profile/1-0.json"))
        validate(self.config, schema)


class ProfileError(Exception):
    """Raised when an error with the Reflekt profile is detected."""

    def __init__(self, message: str, profile: Profile) -> None:
        """Initialize ProfileError class.

        Args:
            message (str): Error message.
            profile (Profile): Reflekt profile class instance.
        """
        self.message = message
        self.profile = profile
        super().__init__(self.message)


if __name__ == "__main__":  # pragma: no cover
    project = Project()
    profile = Profile(project=project)
    profile.validate_profile()
