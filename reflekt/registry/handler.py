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

    def __init__(self, registry: str, select: str, profile: Profile) -> None:
        """Initialize RegistryHandler class.

        Args:
            select (str): The --select argument passed to Reflekt CLI.
            profile (Profile): Reflekt profile to use for registry authentication.
        """
        self.registry = registry
        self.select = select
        self.profile = profile

    def get_registry(self) -> Union[SegmentRegistry, AvoRegistry]:
        """Get registry class based on specified registry type.

        Raises:
            RegistryError: Invalid registry type provided.

        Returns:
            SegmentRegistry | AvoRegistry: Registry class for specified registry type.
        """

        if self.registry == RegistryEnum.segment:
            registry = SegmentRegistry(profile=self.profile)
        elif self.registry == RegistryEnum.avo:
            registry = AvoRegistry(profile=self.profile)
        else:
            raise RegistryError(
                message=(
                    f"CLI argument '--registry {self.select}' is not a supported "
                    f"schema registry. Supported schema registries are:\n"
                    f"    - segment\n"
                    f"    - avo"
                ),
                type=self.type,
                profile=self.profile,
            )

        return registry
