# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0


from reflekt.segment.api import SegmentApi
from reflekt.reflekt.project import ReflektProject
from reflekt.reflekt.config import ReflektConfig


class ReflektApiHandler:
    def __init__(self):
        self._config = ReflektConfig()
        self._cdp = self._config.cdp
        self._cdp_name = self._config.cdp_name

    @property
    def api(self):
        return self._get_api()

    def _get_api(self):
        if self._cdp_name == "avo":
            pass

        elif self._cdp_name == "iteratively":
            pass

        elif self._cdp_name == "rudderstack":
            pass

        elif self._cdp_name == "segment":
            api = SegmentApi(
                workspace_name=self._cdp["segment"]["workspace_name"],
                access_token=self._cdp["segment"]["access_token"],
            )

        elif self._cdp_name == "snowplow":
            pass

        return api
