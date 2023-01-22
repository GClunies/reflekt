# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Union

from reflekt.constants import RegistryEnum
from reflekt.errors import RegistryError
from reflekt.profile import Profile
from reflekt.registry.avo import AvoRegistry
from reflekt.registry.segment import SegmentRegistry


class RegistryHandler:
    """Handler to initialize a registry class based on provided registry type."""

    def __init__(self, select: str, profile: Profile) -> None:
        """Initialize RegistryHandler class.

        Args:
            select (str): The --select argument passed to Reflekt CLI.
            profile (Profile): Reflekt profile to use for registry authentication.
        """
        self.select = select
        self.type = select.split("/")[0]
        self.profile = profile

    def get_registry(self) -> Union[SegmentRegistry, AvoRegistry]:
        """Get registry class based on specified registry type.

        Raises:
            RegistryError: Invalid registry type provided.

        Returns:
            SegmentRegistry | AvoRegistry: Registry class for specified registry type.
        """

        if self.type == RegistryEnum.segment:
            registry = SegmentRegistry(profile=self.profile)
        elif self.type == RegistryEnum.avo:
            registry = AvoRegistry(profile=self.profile)
        else:
            raise RegistryError(
                message=(
                    f"CLI argument '--select {self.select}' starts with '{self.type}' "
                    "which is not a supported schema registry identifier. Valid "
                    "schema registry identifiers are:\n"
                    f"    - segment\n"
                    f"    - avo"
                ),
                type=self.type,
                profile=self.profile,
            )

        return registry
