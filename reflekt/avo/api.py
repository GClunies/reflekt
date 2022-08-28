# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Optional

import requests
from loguru import logger
from reflekt.project import ReflektProject
from requests.auth import HTTPBasicAuth


class AvoApi:
    def __init__(
        self,
        workspace_id: str,
        service_account_name: str,
        service_account_secret: str,
    ) -> None:
        self.type = "avo"
        self.workspace_id = workspace_id
        self.service_account_name = service_account_name
        self.service_account_secret = service_account_secret
        self.base_url = f"https://api.avo.app/workspaces/{workspace_id}/"

    def _get_avo_branch_id(self, avo_branch: Optional[str] = None):
        if avo_branch is None or avo_branch == "main":
            branch_id = "main"
        else:
            try:
                branch_id = ReflektProject().tracking_plans["avo"]["branches"][
                    avo_branch
                ]
            except KeyError:
                logger.error(
                    f"Avo branch '{avo_branch}' not defined in reflekt_project.yml. "
                    f"See Reflekt docs (https://bit.ly/reflekt-project-config) for "
                    f"details on Avo tracking plan and branch configuration."
                )
                raise SystemExit(1)

        return branch_id

    def get(self, avo_branch: str) -> None:
        branch_id = self._get_avo_branch_id(avo_branch)
        url = self.base_url + f"branches/{branch_id}/export/v1"
        r = requests.get(
            url=url,
            auth=HTTPBasicAuth(self.service_account_name, self.service_account_secret),
        )

        return r.json()
