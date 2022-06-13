# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Optional

import requests
from requests import Response

from reflekt.config import ReflektConfig
from reflekt.segment.errors import SegmentApiError


class SegmentApi:
    def __init__(self, workspace_name: str, access_token: str):
        self._config = ReflektConfig()
        self.type = self._config.plan_type
        self.workspace_name = workspace_name
        self.access_token = access_token
        self.base_url = (
            f"https://platform.segmentapis.com/v1beta/workspaces/"
            f"{workspace_name}/tracking-plans/"
        )

    def _list_plans(self):
        url, headers = self._setup_url_headers()
        r = requests.get(url=url, headers=headers)
        self._handle_response(r)
        plans = r.json().get("tracking_plans")
        name_to_id = {
            plan.get("display_name"): plan.get("name").split("/")[-1] for plan in plans
        }
        id_to_name = {
            plan.get("name").split("/")[-1]: plan.get("display_name") for plan in plans
        }

        return name_to_id, id_to_name

    def _get_plan_id_from_name(self, plan_name: str, name_to_id_dict: dict):
        try:
            return name_to_id_dict[plan_name]
        except KeyError:
            return None

    def _setup_url_headers(self, plan_id: Optional[str] = None):
        if plan_id is None:
            url = self.base_url
        else:
            url = self.base_url + plan_id

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        return url, headers

    def _handle_response(self, response: Response):
        response_dict = json.loads(response.text.encode("utf8"))
        if "error" in response_dict:
            raise SegmentApiError(
                f"\n\nSegment Config API error encountered during sync. "
                f"\n    Error type: {response_dict['error']}"
                f"\n    Error code: {response_dict['code']}"
                f"\n    See https://segment.com/docs/config-api/api-design/#errors "  # noqa: E501
                f"for error descriptions."
            )

    def get(self, plan_name: str):
        name_to_id, _ = self._list_plans()
        plan_id = self._get_plan_id_from_name(plan_name, name_to_id)

        if plan_id is None:
            raise SegmentApiError(f"Tracking plan '{plan_name}' was not found.")
        else:
            url, headers = self._setup_url_headers(plan_id=plan_id)

        url, headers = self._setup_url_headers(plan_id=plan_id)
        r = requests.get(url=url, headers=headers)
        self._handle_response(r)

        return r.json()

    def sync(self, plan_name: str, json_plan: dict, dry: bool = False):
        name_to_id, _ = self._list_plans()
        plan_id = self._get_plan_id_from_name(plan_name, name_to_id)
        payload = json.dumps(json_plan)

        if plan_id is None:
            if dry:
                return json_plan
            else:
                url, headers = self._setup_url_headers()
                r = requests.post(url=url, headers=headers, data=payload)
                self._handle_response(r)
        else:
            if dry:
                return json_plan
            else:
                url, headers = self._setup_url_headers(plan_id)
                r = requests.put(url=url, headers=headers, data=payload)
                self._handle_response(r)
