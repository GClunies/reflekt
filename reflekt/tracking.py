# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
# SPDX-License-Identifier: Apache-2.0
#
# SPDX-FileCopyrightText: 2021 dbt Labs, inc.
# SPDX-License-Identifier: Apache-2.0
#
# This file contains derivative works based on:
# https://github.com/dbt-labs/dbt-core/blob/main/core/dbt/tracking.py
#
# Relevant License and Copyright information for this code is found in the
# comment headers above and the ./reuse directory of this repository. All changes are
# licensed under Apache-2.0.

import os
import uuid
from pathlib import Path
from typing import Optional

# import rudder_analytics
import yaml

import segment.analytics as segment_analytics  # FOR DEBUGGING, use 'import analytics as segment_analytics'  # noqa: E501


# Tracking error handling (Segment/Rudderstack)
def on_error(error, items):
    print("An error occurred:", error)


# Setup Segment
if os.getenv("REFLEKT_DEV_SEGMENT_WRITE_KEY") is not None:
    segment_analytics.write_key = os.getenv("REFLEKT_DEV_SEGMENT_WRITE_KEY")
    segment_analytics.debug = True
    segment_analytics.on_error = on_error

else:
    segment_analytics.write_key = "2r0G0DfAXeRZ9ZUhfa9Xk1Hk3FnO2GnW"

# Setup Rudderstack  #TODO - enable after rudderstack merges this PR: https://github.com/rudderlabs/rudder-sdk-python/pull/12  # noqa: E501
# if os.getenv("REFLEKT_DEV_RUDDERSTACK_WRITE_KEY") is not None:
#     rudder_analytics.write_key = os.getenv("REFLEKT_DEV_RUDDERSTACK_WRITE_KEY")
# else:
#     rudder_analytics.write_key = "2EGTUMSUXYUpSRS4uO2sSgfDntI"

# rudder_analytics.data_plane_url = "https://reflektgrwicz.dataplane.rudderstack.com"


class ReflektUser:
    def __init__(self, cookie_dir):
        self.do_not_track = True
        if cookie_dir is not None:
            self.cookie_dir = Path(cookie_dir)
            self.cookie_path = self.cookie_dir / ".user.yml"
            self.id = None

    def state(self):
        return "do not track" if self.do_not_track else "tracking"

    def initialize(self):
        self.do_not_track = False
        cookie = self.get_cookie()
        self.id = cookie.get("id")

    def disable_tracking(self):
        self.do_not_track = True
        self.id = None
        self.cookie_dir = None

    def set_cookie(self):
        # If the user points Reflekt to a folder which exists AND
        # contains a reflekt_config.yml file, then set a cookie. If the
        # specified folder does not exist, or if there is not a reflekt_config.yml
        # file in this folder, then an anonymous_id can be set. This anonymous_id
        # will change in every Reflekt invocation until the user points to a
        # folder which contains a valid reflekt_config.yml file.
        user = {"id": str(uuid.uuid4())}
        cookie_path = self.cookie_dir.absolute()
        profiles_file = cookie_path / "reflekt_config.yml"

        if cookie_path.exists() and profiles_file.exists():
            with open(self.cookie_path, "w") as f:
                yaml.dump(user, f)

        return user

    def get_cookie(self):
        if not self.cookie_path.is_file():
            user = self.set_cookie()
        else:
            with open(self.cookie_path, "r") as f:
                try:
                    user = yaml.safe_load(f)
                    if user is None:
                        user = self.set_cookie()
                except yaml.reader.ReaderError:
                    user = self.set_cookie()

        return user


active_user: Optional[ReflektUser] = None  # By default, no active user


def disable_tracking():
    global active_user
    if active_user is not None:
        active_user.disable_tracking()
    else:
        active_user = ReflektUser(None)


def do_not_track():
    global active_user
    active_user = ReflektUser(None)


def initialize_tracking():
    global active_user
    cookie_dir = Path.home() / ".reflekt"  # Always keep the cookie here

    if not cookie_dir.exists():
        cookie_dir.mkdir(parents=True)

    active_user = ReflektUser(cookie_dir)

    try:
        active_user.initialize()
    except Exception:
        active_user = ReflektUser(None)


def track_event(event_name: str, properties: dict, context: dict):
    global active_user
    if active_user.id is not None:
        segment_analytics.track(active_user.id, event_name, properties, context)
        # rudder_analytics.track(active_user.id, event_name, properties, context)
