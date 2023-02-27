# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import os
import uuid
from pathlib import Path
from typing import Optional

import segment.analytics as segment_analytics  # FOR DEBUGGING, use 'import analytics as segment_analytics'  # noqa: E501
import yaml
from loguru import logger


# Tracking error handling (Segment/Rudderstack)
def on_error(error):
    """Log debugging error from Segment/Rudderstack.

    Args:
        error (Any): The error.
    """
    logger.error("An error occurred:", error)


# Setup Segment
if os.getenv("REFLEKT_SEGMENT_WRITE_KEY_DEV") is not None:
    segment_analytics.write_key = os.getenv("REFLEKT_SEGMENT_WRITE_KEY_DEV")
    segment_analytics.debug = True
    segment_analytics.on_error = on_error
else:
    segment_analytics.write_key = "2r0G0DfAXeRZ9ZUhfa9Xk1Hk3FnO2GnW"


class ReflektUser:
    """Reflekt user class to enable anonymous usage statistics."""

    def __init__(self) -> None:
        """Initialize a Reflekt user with default values."""
        self._cookie_dir: Path = Path.home() / ".reflekt"  # Always keep the cookie here
        self._cookie_path: Path = self._cookie_dir / ".user.yml"
        self.id: Optional[str] = None

    def initialize(self) -> None:
        """Initialize the user. Getting their ID from the cookie file."""
        user = self.get_user_id_cookie()
        self.id = user.get("id")

    def get_user_id_cookie(self):
        """Get the user's ID from the cookie file.

        Returns:
            dict: dict containing user's ID.
        """
        # Cookie dir does not exist, create it
        if not self._cookie_dir.exists():
            self._cookie_dir.mkdir(parents=True)

        # Cookie file does not exist, create it
        if not self._cookie_path.exists():
            self._cookie_path.touch()
            user = {"id": str(uuid.uuid4())}

            with self._cookie_path.open("w") as f:
                yaml.dump(user, f)

        else:  # Cookie file exists
            with self._cookie_path.open("r") as f:
                try:  # Try to load cookie
                    user = yaml.safe_load(f)
                    if user is None:  # Cookie is empty, set ID
                        user = {"id": str(uuid.uuid4())}
                    elif user.get("id") is None:  # Cookie does not have ID, set it
                        user = {"id": str(uuid.uuid4())}
                except yaml.reader.ReaderError:  # Error reading cookie file, create it
                    user = {"id": str(uuid.uuid4())}

        # Overwrite cookie to ensure it always exists. Even if it's the same.
        with self._cookie_path.open("w") as f:
            yaml.dump(user, f)

        return user


# NOTE - no need to call identify() since user ID is set via a cookie
def track_event(user_id: str, event_name: str, properties: dict, context: dict):
    """Track an event.

    Args:
        user_id (str): The user's ID.
        event_name (str): The event name.
        properties (dict): The event properties.
        context (dict): The event context.
    """
    segment_analytics.track(user_id, event_name, properties, context)
