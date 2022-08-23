# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from loguru import logger

from reflekt.avo.api import AvoApi
from reflekt.config import ReflektConfig
from reflekt.constants import PLANS
from reflekt.project import ReflektProject
from reflekt.segment.api import SegmentApi


class ReflektApiHandler:
    """A class that handles which CDP or Analytics Governance API to use when
    pulling or pushing tracking plans using `reflekt pull` and `reflekt push`
    """

    def __init__(self) -> None:
        self._project = ReflektProject()
        self._config = ReflektConfig()
        self.type: str = self._config.plan_type

    def get_api(self):
        if self._config.plan_type == "segment":
            return SegmentApi(
                workspace_name=self._config.workspace_name,
                access_token=self._config.access_token,
            )
        elif self._config.plan_type == "avo":
            return AvoApi(
                # TODO
                # 1. Add to Avo config profile
                # 2. Update reflekt init to prompt user for service account credentials
                workspace_id=self._config.workspace_id,
                service_account_name=self._config.service_account_name,
                service_account_secret=self._config.service_account_secret,
            )
        # elif self._config.plan_type == "rudderstack":
        #     pass
        # elif self._config.plan_type == "snowplow":
        #     pass
        else:
            logger.error(
                f"Tracking plan type '{self._config.plan_type}' defined in "
                f"{self._config.path} is not supported by Reflekt. Supported tracking "
                f"plan types are: {PLANS}"
            )
