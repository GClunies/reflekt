# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Optional

from reflekt.avo.cli import AvoCli
from reflekt.config import ReflektConfig
from reflekt.segment.api import SegmentApi


class ReflektApiHandler:
    """A class that handles which CDP or Analytics Governance API to use when
    pulling or pushing tracking plans using `reflekt pull` and `reflekt push`
    """

    def __init__(self) -> None:
        self._config = ReflektConfig()
        self.type: str = self._config.plan_type

    def get_api(self, avo_branch: Optional[str] = None):
        if self._config.plan_type == "avo":
            return AvoCli(  # Not CLI (not API), but called via get_api for consistency
                avo_branch
            )
        elif self._config.plan_type == "iteratively":
            pass
        elif self._config.plan_type == "rudderstack":
            pass
        elif self._config.plan_type == "segment":
            return SegmentApi(
                workspace_name=self._config.workspace_name,
                access_token=self._config.access_token,
            )
        elif self._config.plan_type == "snowplow":
            pass
