# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from requests import Response

from reflekt.constants import RegistryEnum
from reflekt.profile import Profile


class SelectArgError(Exception):
    """Raised when an invalid --select argument is provided."""

    def __init__(self, message: str, select: str) -> None:
        """Initialize SelectArgError class.

        Args:
            message (str): Error message.
            select (str): The invalid --select argument.
        """
        self.message = message
        self.select = select
        super().__init__(self.message)


class SourceArgError(Exception):
    """Raised when an invalid --source argument is provided."""

    def __init__(self, message: str, source: str) -> None:
        """Initialize SourceArgError class.

        Args:
            message (str): Error message.
            source (str): The invalid --source argument.
        """
        self.message = message
        self.source = source
        super().__init__(self.message)


class RegistryError(Exception):
    """Raised when an error with the specified registry is detected."""

    def __init__(self, message: str, type: RegistryEnum, profile: Profile) -> None:
        """Initialize InvalidRegistryError class.

        Args:
            message (str): Error message.
            type (RegistryEnum): Type of schema registry.
            profile (Profile): Reflekt profile object.
        """
        self.message = message
        self.type = type
        self.profile = profile
        super().__init__(self.message)


class ApiResponseError(Exception):
    """Raised when an API response returns a non-successful status code."""

    def __init__(self, message: str, response: Response) -> None:
        """Initialize ApiError class.

        Args:
            message (str): Error message.
            response (Response): Response object.
        """
        self.message = message
        self.response = response
        super().__init__(self.message)


class LintingError(Exception):
    """Raised when a linting error is encountered."""

    def __init__(self, message: str) -> None:
        """Initialize LintingError class.

        Args:
            message (str): Error message.
        """
        self.message = message
        super().__init__(self.message)
