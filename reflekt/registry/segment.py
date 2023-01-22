# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import copy
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

import requests
from inflection import titleize
from loguru import logger
from requests import Response
from rich import print
from rich.traceback import install

from reflekt import SHOW_LOCALS
from reflekt.casing import event_case
from reflekt.constants import REFLEKT_JSON_SCHEMA
from reflekt.errors import ApiResponseError, RegistryError, SelectArgError
from reflekt.profile import Profile
from reflekt.project import Project


install(show_locals=SHOW_LOCALS)

SEGMENT_JSON_SCHEMA = {
    "key": "",  # Schema name
    "type": "",  # TRACK/IDENTIFY/GROUP
    "version": 1,  # Version number
    "jsonSchema": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "labels": {},
        "description": "",
        "properties": {
            "context": {},
            "traits": {},
            "properties": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
}


class SegmentRegistry:
    """Class with methods for interacting with Segment's schema registry."""

    def __init__(self, profile: Profile) -> None:
        """Initialize SegmentRegistry class.

        Args:
            profile (Profile): Reflekt Profile object.

        Raises:
            RegistryError: Segment Protocols registry config is missing from
                reflekt_profiles.yml.
        """
        self.profile = profile
        self.type = "segment"
        self.config_exists = False  # Assume config does not exist
        self.base_url: str = "https://api.segmentapis.com/tracking-plans"

        for registry in self.profile.registry:
            if registry["type"] == self.type:
                self.config_exists = True  # Config exists
                self.registry = registry
                self.api_token = registry["api_token"]
                self.headers: dict = {
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                }

        if not self.config_exists:
            raise RegistryError(
                message=(
                    f"Schema Registry of '{self.type}' not found in {self.profile.path}"
                ),
                type=self.type,
                profile=self.profile,
            )

    def _get_plans(self) -> List:
        """Retrieve list of dicts describing tracking plans and their attributes.

        Returns:
            List: A list of dicts describing tracking plans and their attributes.
        """
        r = requests.get(
            url=self.base_url, headers=self.headers, params={"pagination[count]": 200}
        )
        data = self._handle_response(r)

        return data["trackingPlans"]

    def _get_plan_id(self, plan_name: str) -> str:
        """Get tracking plan ID from plan name as it appears in Segment Protocols.

        The plan ID uniquely identifies the tracking plan on Segment's servers.

        Args:
            plan_name (str): The name of the tracking plan.

        Returns:
            str: The ID of the tracking plan.
        """
        plans = self._get_plans()

        for plan in plans:
            if plan["name"] == plan_name:
                plan_id = plan["id"]
                break  # Exit loop once plan ID is found
            else:
                plan_id = None

        return plan_id

    def _parse_select(self, select: str) -> Tuple[str, str, int]:
        """Parse --select arg into a tuple of (plan_name, schema_name, schema_ver).

        Args:
            select (str): The --select arg passed to Reflekt CLI.

        Raises:
            SelectArgError: The --select arg is not compatible with Segment.

        Returns:
            Tuple[str, str, int]: A tuple of (plan_name, schema_name, schema_ver).
        """
        select_error_msg = (
            f"Invalid --select argument: {select}\n"  # noqa: E501
            f"When pulling from Segment schema registry, --select args must follow the format(s):\n"  # noqa: E501
            f"   --select segment/plan_name                             # all schemas from a plan_name\n"  # noqa: E501
            f"   --select segment/plan_name/schema_name                 # schema_name in plan_name\n"  # noqa: E501
            f"   --select segment/plan_name/schema_name/schema_version  # schema_version for schema_name in plan_name"  # noqa: E501
        )

        if select.split("/")[0] != str.lower("segment"):
            raise SelectArgError(message=select_error_msg, select=select)

        if len(select.split("/")) > 4 or len(select.split("/")) < 2:
            raise SelectArgError(message=select_error_msg, select=select)

        if len(select.split("/")) == 2:
            plan_name = select.split("/")[1]
            schema_name = None
            schema_model_version = None
        elif len(select.split("/")) == 3:
            plan_name = select.split("/")[1]
            schema_name = select.split("/")[2]
            schema_model_version = None
        elif len(select.split("/")) == 4:
            plan_name = select.split("/")[1]
            schema_name = select.split("/")[2]
            raw_schema_version = select.split("/")[3]

            schema_model_version = int(raw_schema_version.split("-")[0])
            schema_revision_version = int(raw_schema_version.split("-")[1])
            schema_addition_version = int(
                raw_schema_version.split("-")[2].replace(".json", "")
            )

            if schema_revision_version > 0 or schema_addition_version > 0:
                raise SelectArgError(
                    message=(
                        f"Invalid argument '--select {select}' provided to CLI.\n"  # noqa: E501
                        f"Segment schema registry only supports MODEL version numbers (e.g., MODEL-ADDITION.json):\n"  # noqa: E501
                        f"    Valid: 1-0, 2-0, 3-0, etc.\n"
                        f"    Invalid: 1-1, 2-1, 3-7, etc."
                    ),
                    select=select,
                )

        return plan_name, schema_name, schema_model_version

    def _handle_response(self, response: Response) -> Dict:
        """Handle response from the Segment API, returning requested data as a dict.

        Args:
            response (Response): A response from the Segment API.

        Raises:
            ApiResponseError: An error occurred when handling the response.

        Returns:
            Dict: The data requested from the Segment API.
        """
        if response.status_code not in [200, 201]:
            raise ApiResponseError(
                message=(
                    "Segment API returned an error (see docs for details: https://docs.segmentapis.com/tag/Error-Handling#section/Status-codes-overview).\n"  # noqa: E501
                    f"    Status Code: {response.status_code}\n"
                    f"    Reason: {response.reason}\n"
                ),
                response=response,
            )

        return response.json()["data"]

    def _pull_segment(self, select: str) -> List:
        """Fetch Segment tracking plan schemas from API based on --select from CLI.

        Args:
            select (str): The --select argument passed to Reflekt CLI.

        Raises:
            SelectArgError: Error with the --select argument.

        Returns:
            List: Tracking plan schemas from Segment Protocols.
        """
        logger.info("Searching Segment for schemas")
        print("")
        plan_name, schema_name, schema_version = self._parse_select(select)
        plan_id = self._get_plan_id(plan_name)
        r = requests.get(
            url=self.base_url + f"/{plan_id}/rules",
            headers=self.headers,
            params={"pagination[count]": 200},
        )
        plan = self._handle_response(r)
        s_schemas = [
            rule for rule in plan["rules"] if rule["type"] not in ["COMMON", "ALIAS"]
        ]

        if schema_name is not None:
            s_schemas = [
                s_schema
                for s_schema in s_schemas
                if s_schema["key"] == schema_name
                or str.lower(s_schema["type"]) == str.lower(schema_name)
            ]

        if schema_version is not None:
            s_schemas = [
                s_schema
                for s_schema in s_schemas
                if s_schema["version"] == schema_version
            ]

        if len(s_schemas) == 0:
            raise SelectArgError(
                message=(f"No Segment schemas found for: --select {select}\n"),
                select=select,
            )
        else:
            logger.info(f"Found {len(s_schemas)} schemas to pull:")
            print("")

        return s_schemas

    def _push_segment(
        self, select: str, plan_name: str, schemas: List, delete: bool = False
    ) -> None:
        """Sync Reflekt schemas to Segment Protocols based on --select from CLI.

        If the tracking plan does not exist, it will be created.

        Args:
            select (str): The --select argument passed to Reflekt CLI.
            plan_name (str): The name of the tracking plan.
            schemas (List): A list of schemas to be updated in the tracking plan.
            delete (bool): Flag to delete the schemas identified by the --select
                argument.
        """

        plan_name, schema_name, _ = self._parse_select(select)
        plan_id = self._get_plan_id(plan_name=plan_name)

        if not delete:  # Add/Update schemas
            if plan_id is None:  # Create new tracking plan if it doesn't exist
                r = requests.post(
                    url=self.base_url,
                    headers=self.headers,
                    json={"name": plan_name, "type": "LIVE"},
                )
                plan_data = self._handle_response(r)
                plan_id = plan_data["trackingPlan"]["id"]

            if schema_name is None:  # Update all schemas in tracking plan
                r = requests.put(
                    url=self.base_url + f"/{plan_id}/rules",
                    headers=self.headers,
                    json={"trackingPlanId": plan_id, "rules": schemas},
                )
            elif schema_name is not None:  # Update specified schema(s) in tracking plan
                r = requests.patch(
                    url=self.base_url + f"/{plan_id}/rules",
                    headers=self.headers,
                    json={"trackingPlanId": plan_id, "rules": schemas},
                )
        else:  # Delete schemas
            r = requests.delete(
                url=self.base_url + f"/{plan_id}/rules",
                headers=self.headers,
                json={"trackingPlanId": plan_id, "rules": schemas},
            )

        self._handle_response(r)
        print("")
        logger.info("[green]Completed successfully[green/]")

    def pull(self, select: str) -> None:
        """Pull schemas from Segment Protocols and write to Reflekt JSON schemas files.

        Args:
            select (str): The --select argument passed to Reflekt CLI.
        """
        plan_name, _, _ = self._parse_select(select)
        s_schemas = self._pull_segment(select=select)  # Segment schemas

        for i, s_schema in enumerate(s_schemas, start=1):
            if s_schema["type"] in ["IDENTIFY", "GROUP"]:
                name = (
                    event_case(s_schema["type"])
                    if self.profile.project.conventions["event"]["casing"] != "any"
                    else titleize(  # This is how it appears in Segment Protocols
                        s_schema["type"]
                    )
                )
                description = f"Segment {str.lower(s_schema['type'])}() call."
                metadata = s_schema["jsonSchema"].get("labels", {})
                properties = (
                    s_schema["jsonSchema"]
                    .get("properties", {})
                    .get("traits", {})
                    .get("properties", {})
                )
                required = (
                    s_schema["jsonSchema"]
                    .get("properties", {})
                    .get("traits", {})
                    .get("required", [])
                )
                additional_properties = (
                    s_schema["jsonSchema"]
                    .get("properties", {})
                    .get("traits", {})
                    .get("additionalProperties", False)
                )
            elif s_schema["type"] == "TRACK":
                name = s_schema["key"]
                description = s_schema["jsonSchema"]["description"]
                metadata = s_schema["jsonSchema"].get("labels", {})
                properties = (
                    s_schema["jsonSchema"]
                    .get("properties", {})
                    .get("properties", {})
                    .get("properties", {})
                )
                required = (
                    s_schema["jsonSchema"]
                    .get("properties", {})
                    .get("properties", {})
                    .get("required", [])
                )
                additional_properties = (
                    s_schema["jsonSchema"]
                    .get("properties", {})
                    .get("properties", {})
                    .get("additionalProperties", False)
                )

                if properties != {}:  # Cleanup 'type:' formatting
                    for key, _ in properties.items():
                        if "type" in properties[key]:
                            if len(properties[key]["type"]) == 1:  # Convert list to str
                                properties[key]["type"] = properties[key]["type"][0]

            version = f"{str(s_schema['version'])}-0"
            id = f"{self.type}/{plan_name}/{name}/{version}.json"

            # Copy empty Reflekt jsonschema and set values
            r_schema = copy.deepcopy(REFLEKT_JSON_SCHEMA)
            r_schema["$id"] = id
            r_schema["self"]["vendor"] = self.profile.project.vendor
            r_schema["self"]["name"] = name
            r_schema["description"] = description
            r_schema["self"]["version"] = version
            r_schema["properties"] = properties
            r_schema["required"] = required
            r_schema["additionalProperties"] = additional_properties
            r_schema["metadata"] = metadata

            write_path = Path(self.profile.project.dir / "schemas" / r_schema["$id"])

            if not write_path.parent.exists():
                write_path.parent.mkdir(parents=True)

            logger.info(
                f"{i} of {len(s_schemas)} Writing to [magenta]{write_path}[magenta/]"
            )
            with open(write_path, "w", encoding="utf-8") as f:
                json.dump(r_schema, f, indent=4, ensure_ascii=False)

        print("")
        logger.info("[green]Completed successfully[green/]")

    def push(self, select: str, delete: bool = False) -> None:
        """Push Reflekt JSON schemas to Segment Protocols.

        Args:
            select (str): The --select argument passed to Reflekt CLI.
            delete (bool): Flag to delete the schemas identified by the --select
                argument.

        Raises:
            SelectArgError: Error with the --select argument.
        """
        plan_name, _, schema_version = self._parse_select(select)

        if schema_version is not None:
            select = f"{select}.json"

        project = Project()
        schema_paths = []  # List of schema paths to push
        s_schemas = []  # Segment schemas
        r_schemas = []  # Reflekt schemas
        select_path = project.dir / "schemas" / select
        logger.info(f"Searching for JSON schemas in: {str(select_path)}")
        print("")

        if select_path.is_dir():  # Get all schemas in directory
            for root, _, files in os.walk(select_path):
                for file in files:
                    if file.endswith(".json"):
                        schema_paths.append(Path(root) / file)
        else:  # Get single schema file
            if select_path.exists():
                schema_paths.append(select_path)

        for schema_path in schema_paths:  # Get all Reflekt schemas
            with schema_path.open("r") as f:
                r_schemas.append(json.load(f))

        if len(r_schemas) == 0:
            raise SelectArgError(
                message=(f"No JSON schemas found for: --select {select}\n"),
                select=select,
            )
        else:
            logger.info(f"Found {len(r_schemas)} schemas to push")
            print("")

        for i, r_schema in enumerate(r_schemas, start=1):
            schema_path = self.profile.project.dir / "schemas" / r_schema["$id"]
            logger.info(
                f"{i} of {len(schema_paths)} Pushing "
                f"[magenta]{schema_path}[magenta/]"
            )
            if str.lower(r_schema["self"]["name"]) in ["identify", "group"]:
                s_schema = copy.deepcopy(SEGMENT_JSON_SCHEMA)
                s_schema["type"] = r_schema["self"]["name"].upper()
                s_schema["version"] = int(r_schema["self"]["version"].split("-")[0])
                s_schema["jsonSchema"]["properties"]["traits"]["properties"] = r_schema[
                    "properties"
                ]
                s_schema["jsonSchema"]["properties"]["traits"]["required"] = r_schema[
                    "required"
                ]
                s_schema["jsonSchema"]["properties"]["traits"][
                    "additionalProperties"
                ] = r_schema["additionalProperties"]
            else:
                s_schema = copy.deepcopy(SEGMENT_JSON_SCHEMA)
                s_schema["key"] = r_schema["self"]["name"]
                s_schema["type"] = "TRACK"
                s_schema["version"] = int(r_schema["self"]["version"].split("-")[0])
                s_schema["jsonSchema"]["labels"] = r_schema["metadata"]
                s_schema["jsonSchema"]["description"] = r_schema["description"]
                s_schema["jsonSchema"]["properties"]["properties"][
                    "properties"
                ] = r_schema["properties"]
                s_schema["jsonSchema"]["properties"]["properties"][
                    "required"
                ] = r_schema["required"]
                s_schema["jsonSchema"]["properties"]["properties"][
                    "additionalProperties"
                ] = r_schema["additionalProperties"]

            s_schemas.append(s_schema)

        self._push_segment(
            select=select, plan_name=plan_name, schemas=s_schemas, delete=delete
        )


if __name__ == "__main__":  # pragma: no cover
    project = Project()
    profile = Profile(project=project)
    registry = SegmentRegistry(profile=profile)

    # --- PULL SEGMENT TO REFLEKT ---
    # registry.pull(select="segment/ecommerce")

    # --- PUSH REFLEKT TO SEGMENT ---
    registry.push(select="segment/ecommerce/CartViewed")
