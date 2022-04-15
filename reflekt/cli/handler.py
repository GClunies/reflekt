# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from reflekt.avo.cli import AvoCli
from reflekt.segment.api import SegmentApi
from reflekt.reflekt.config import ReflektConfig


class ReflektApiHandler:
    def __init__(self):
        self._config = ReflektConfig()
        # self._cdp = self._config.cdp
        self.plan_type = self._config.plan_type
        self.cdp_name = self._config.cdp_name
        self.access_token = self._config.access_token
        self.workspace_name = self._config.workspace_name

    @property
    def api(self):
        return self._get_api()

    def _get_api(self):
        if self.plan_type == "avo":
            # This API class should be abel to `avo pull` to populate the Avo JSON schema
            # It will have a dependency on the Avo cli which is a npm package (not great, but OK)
            # Will need to include docs on hwo to setup this dependency
            api = AvoCli()
            pass

        elif self.plan_type == "iteratively":
            pass

        elif self.plan_type == "rudderstack":
            pass

        elif self.plan_type == "segment":
            api = SegmentApi(
                workspace_name=self.workspace_name,
                access_token=self.access_token,
            )

        elif self.plan_type == "snowplow":
            pass

        return api
