# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import copy
import json
from pathlib import Path
from typing import Dict, List

import requests
from loguru import logger
from requests import Response
from requests.auth import HTTPBasicAuth
from rich import print
from rich.traceback import install

from reflekt import SHOW_LOCALS
from reflekt.constants import REFLEKT_JSON_SCHEMA
from reflekt.errors import ApiResponseError, RegistryError, SelectArgError
from reflekt.profile import Profile
from reflekt.project import Project


install(show_locals=SHOW_LOCALS)


class AvoRegistry:
    """Class with methods for with Avo schema registry."""

    def __init__(self, profile: Profile) -> None:
        """Initialize AvoRegistry class.

        Args:
            profile (Profile): Reflekt Profile object.

        Raises:
            RegistryError: Avo registry configuration is missing from
                reflekt_profiles.yml.
        """
        self.profile = profile
        self.type = "avo"
        self.config_exists = False  # Assume config does not exist

        for registry in self.profile.registry:
            if registry["type"] == self.type:
                self.config_exists = True
                self.workspace_id = registry["workspace_id"]
                self.service_account_name = registry["service_account_name"]
                self.service_account_secret = registry["service_account_secret"]
                self.base_url = f"https://api.avo.app/workspaces/{self.workspace_id}/"

        if not self.config_exists:
            raise RegistryError(
                message=(
                    f"Registry type '{self.type}' not configured in "
                    f"reflekt_profiles.yml at {self.profile.path}"
                ),
                type=self.type,
                profile=self.profile,
            )

    def _get_avo_branch_id(self, branch: str = "main") -> str:
        """Get Avo branch ID from `registry:` config in reflekt_project.yml.

        Args:
            branch (str): Name of the branch in Avo. Must be configured in
                reflekt_project.yml under `registry:` config. Defaults to "main".

        Raises:
            KeyError: The Avo branch is not configured in reflekt_project.yml.

        Returns:
            str: The branch's ID in Avo.
        """
        try:
            if branch != "main":
                branch_id = self.profile.project.registry["avo"]["branches"][branch]
            else:
                branch_id = branch
            return branch_id
        except KeyError:
            raise KeyError(
                f"Branch '{branch}' not configured in reflekt_project.yml at "
                f"{self.profile.project.path}"
            )

    def _parse_select(self, select: str) -> str:
        """Parse the --select argument passed to Reflekt CLI.

        Args:
            select (str): The --select argument passed to Reflekt CLI.

        Raises:
            SelectArgError: The --select arg is not compatible with Avo's schema
                registry.

        Returns:
            str: The Avo branch
        """
        if select.split("/")[0] != str.lower("avo"):
            raise SelectArgError(
                message=(
                    f"Invalid --select argument: {select}\n"
                    f"When pulling from Avo schema registry, --select args must follow the format:\n"  # noqa: E501
                    f"   --select avo/main           # All schemas in 'main' branch\n"  # noqa: E501
                    f"   --select avo/staging        # All schemas in 'staging' branch"  # noqa: E501
                ),
                type=self.type,
                profile=self.profile,
            )

        return select.split("/")[1]

    def _handle_response(self, response: Response) -> Dict:
        """Handle response from the Segment API, returning requested data as a dict.

        Args:
            response (Response): A response from the Segment API.

        Raises:
            ApiResponseError: An error occurred when handling the response.

        Returns:
            Dict: The data requested from the Segment API.
        """
        if response.status_code != 200:
            raise ApiResponseError(
                message=(
                    "Avo API returned an error.\n"  # noqa: E501
                    f"    Status Code: {response.status_code}\n"
                    f"    Reason: {response.reason}\n"
                ),
                response=response,
            )

        return response.json()["events"]

    def pull_avo(self, select: str, branch: str) -> List:
        """Pull tracking plan schemas from Avo.

        Args:
            select (str): The --select argument passed to Reflekt CLI.
            branch (str): Name of tracking plan branch in Avo.

        Raises:
            SelectArgError: Error with the --select argument.

        Returns:
            List: Tracking plan schemas from Avo.
        """
        logger.info("Searching Avo for schemas")
        print("")
        branch_id = self._get_avo_branch_id(branch)
        url = self.base_url + f"branches/{branch_id}/export/v1"
        r = requests.get(
            url=url,
            auth=HTTPBasicAuth(self.service_account_name, self.service_account_secret),
        )
        a_schemas = self._handle_response(r)

        if len(a_schemas) == 0:
            raise SelectArgError(
                message=(f"No JSON schemas found for: --select {select}\n"),
                select=select,
            )
        else:
            logger.info(f"Found {len(a_schemas)} schema(s) to pull")
            print("")

        return a_schemas

    def pull(self, select: str):
        """Pull schemas from Avo and write to Reflekt JSON schemas files.

        Args:
            select (str): The --select argument passed to Reflekt CLI.
        """
        branch = self._parse_select(select=select)
        a_schemas = self.pull_avo(select=select, branch=branch)

        for i, a_schema in enumerate(a_schemas, start=1):
            name = a_schema["name"]
            description = a_schema["description"]
            metadata = a_schema["tags"]
            properties = (
                a_schema["rules"]
                .get("properties", {})
                .get("properties", {})
                .get("properties", {})
            )

            for _, prop_dict in properties.items():
                prop_dict.pop("id", None)  # Remove fields specific to Avo
                prop_dict.pop("index", None)
                prop_dict.pop("nameMapping", None)

            required = (
                a_schema["rules"]
                .get("properties", {})
                .get("properties", {})
                .get("required", [])
            )
            additional_properties = (
                a_schema["rules"]
                .get("properties", {})
                .get("properties", {})
                .get("additionalProperties", False)
            )

            if properties != {}:  # Cleanup 'type:' formatting
                for key, _ in properties.items():
                    if len(properties[key]["type"]) == 1:  # Convert list to str
                        properties[key]["type"] = properties[key]["type"][0]

            version = "1-0"  # Lock version for Avo, only used to build data artifacts
            id = f"{self.type}/{branch}/{name}/{version}.json"

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
                f"{i} of {len(a_schemas)} Writing to [magenta]{write_path}[magenta/]"
            )
            with open(write_path, "w", encoding="utf-8") as f:
                json.dump(r_schema, f, indent=4, ensure_ascii=False)

        print("")
        logger.info("[green]Completed successfully[green/]")


if __name__ == "__main__":  # pragma: no cover
    project = Project()
    profile = Profile(project=project)
    registry = AvoRegistry(profile=profile)

    # --- PULL AVO TO REFLEKT ---
    registry.pull(select="avo/main")
