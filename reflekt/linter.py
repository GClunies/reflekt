# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
from typing import List

from jsonschema import Draft7Validator
from loguru import logger

from reflekt.casing import event_case, property_case
from reflekt.project import Project


class Linter:
    """Reflekt linter class.

    Lints event schemas for naming conventions, required metadata, and other issues.
    """

    def __init__(self, project: Project) -> None:
        """Initialize Reflekt linter.

        Args:
            project (Project): Reflekt project object.
        """
        self._project = project
        self._meta_path = self._project.dir / "schemas/.reflekt/event-meta/1-0.json"

        with self._meta_path.open() as f:
            self._meta_schema = json.load(f)

    def lint_event_name_matches_id(
        self, schema_event_name: str, schema_id: str, errors: List
    ):
        """Check that the schema event name matches the schema ID.

        Args:
            schema_event_name (str): The event name from the schema.
            schema_id (str): Reflekt schema ID.
            errors (List): A list of linting errors.
        """
        abs_path = self._project.dir / "schemas" / schema_id
        name_from_id = schema_id.split("/")[-2]

        if schema_event_name != name_from_id:
            err_msg = (
                f"Event name '{schema_event_name}' does not match schema ID "
                f"'{schema_id}' in {abs_path}"
            )
            logger.error(err_msg)
            errors.append(err_msg)

    def lint_event_version_matches_id(
        self, schema_event_version: str, schema_id: str, errors: List
    ):
        """Check that the schema event version matches the schema ID.

        Args:
            schema_event_version (str): The event version from the schema.
            schema_id (str): Reflekt schema ID.
            errors (List): A list of linting errors.
        """
        abs_path = self._project.dir / "schemas" / schema_id
        version_from_id = schema_id.split("/")[-1].replace(".json", "")

        if schema_event_version != version_from_id:
            err_msg = (
                f"Event version '{schema_event_version}' does not match schema ID "
                f"'{schema_id}' in {abs_path}"
            )
            logger.error(err_msg)
            errors.append(err_msg)

    def lint_event_casing(self, event_name: str, schema_id: str, errors: List):
        """Check that the event name is in the correct casing.

        Args:
            event_name (str): The event name.
            schema_id (str): Reflekt schema ID.
            errors (List): A list of linting errors.
        """
        abs_path = self._project.dir / "schemas" / schema_id
        if event_name != event_case(event_name):
            err_msg = (
                f"Event '{event_name}' in {abs_path} does not match naming convention "
                f"'casing: {self._project.conventions['event']['casing']}' in "
                f"{self._project.path}. "
            )
            logger.error(err_msg)
            errors.append(err_msg)

    def lint_event_numbers(self, event_name: str, schema_id: str, errors: List):
        """Check that the event name does not contain numbers.

        Args:
            event_name (str): The event name.
            schema_id (str): Reflekt schema ID.
            errors (List): A list of linting errors.
        """
        abs_path = self._project.dir / "schemas" / schema_id
        if any(char.isdigit() for char in event_name):
            err_msg = (
                f"Event '{event_name}' in {abs_path} does not match naming convention "
                f"'numbers: {self._project.conventions['event']['numbers']}' in "
                f"{self._project.path}. "
            )
            logger.error(err_msg)
            errors.append(err_msg)

    def lint_event_reserved(self, event_name: str, schema_id: str, errors: List):
        """Check that the event name is not a reserved name.

        Args:
            event_name (str): The event name.
            schema_id (str): Reflekt schema ID.
            errors (List): A list of linting errors.
        """
        abs_path = self._project.dir / "schemas" / schema_id
        if event_name in self._project.conventions["event"]["reserved"]:
            err_msg = (
                f"Event '{event_name}' in {abs_path} is a reserved name in convention "
                f"in {self._project.path}. Reserved event names are:\n"
                f"    'reserved: {self._project.conventions['event']['reserved']}'"
            )
            logger.error(err_msg)
            errors.append(err_msg)

    def lint_property_casing(self, prop_name: str, schema_id: str, errors: List):
        """Check that the property name is in the correct casing.

        Args:
            prop_name (str): The property name.
            schema_id (str): Reflekt schema ID.
            errors (List): A list of linting errors.
        """
        abs_path = self._project.dir / "schemas" / schema_id
        if prop_name != property_case(prop_name):
            err_msg = (
                f"Property '{prop_name}' in {abs_path} does not match naming "
                f"convention "
                f"'casing: {self._project.conventions['property']['casing']}' in "
                f"{self._project.path}."
            )
            logger.error(err_msg)
            errors.append(err_msg)

    def lint_property_numbers(self, prop_name: str, schema_id: str, errors: List):
        """Check that the property name does not contain numbers.

        Args:
            prop_name (str): The property name.
            schema_id (str): Reflekt schema ID.
            errors (List): A list of linting errors.
        """
        abs_path = self._project.dir / "schemas" / schema_id
        if any(char.isdigit() for char in prop_name):
            err_msg = (
                f"Property '{prop_name}' in {abs_path} does not match naming "
                f"convention "
                f"'numbers: {self._project.conventions['property']['numbers']}' in "
                f"{self._project.path}."
            )
            logger.error(err_msg)
            errors.append(err_msg)

    def lint_property_reserved(self, prop_name: str, schema_id: str, errors: List):
        """Check that the property name is not a reserved name.

        Args:
            prop_name (str): The property name.
            schema_id (str): Reflekt schema ID.
            errors (List): A list of linting errors.
        """
        abs_path = self._project.dir / "schemas" / schema_id
        if prop_name in self._project.conventions["property"]["reserved"]:
            err_msg = (
                f"Property '{prop_name}' in {abs_path} is a reserved name in "
                f"{self._project.path}. Reserved property names are:\n"
                f"    'reserved: {self._project.conventions['property']['reserved']}'"
            )
            logger.error(err_msg)
            errors.append(err_msg)

    def lint_property_description(
        self, prop_name: str, description: str, schema_id: str, errors: List
    ):
        """Check that the property description is not empty.

        Args:
            prop_name (str): The property name.
            description (str): The property description.
            schema_id (str): Reflekt schema ID.
            errors (List): A list of linting errors.
        """
        abs_path = self._project.dir / "schemas" / schema_id
        if not description:
            err_msg = (
                f"Property '{prop_name}' in {abs_path} does not have a description."
            )
            logger.error(err_msg)
            errors.append(err_msg)

    def lint_property_type(
        self, prop_name: str, prop_type_list: list, schema_id: str, errors: List
    ):
        """Check that the property data type is valid.

        Args:
            prop_name (str): The property name.
            prop_type_list (list): List of valid property data types.
            schema_id (str): Reflekt schema ID.
            errors (List): A list of linting errors.
        """
        abs_path = self._project.dir / "schemas" / schema_id
        for prop_type in prop_type_list:
            if prop_type not in self._project.conventions["data_types"]:
                err_msg = (
                    f"Property '{prop_name}' in schema '{abs_path}' has type "
                    f"'{prop_type}' which is not allowed per the config in "
                    f"reflekt_self._project.yml:\n "
                    f"    'data_types: {self._project.conventions['data_types']}'"
                )
                logger.error(err_msg)
                errors.append(err_msg)

    def lint_schema(self, r_schema: dict, errors: list):
        """Lint event schema.

        Linting is performed against conventions defined in reflekt_self._project.yml
        and required metadata fields defined in schemas/.reflekt/event-meta/1-0.json.

        If a linting error is found, the error message is appended to the errors list.

        Args:
            r_schema (dict): The schema to lint.
            errors (list): A list to append linting errors to.

        Returns:
            errors (list): A list of linting errors.
        """
        schema_path = self._project.dir / "schemas" / r_schema["$id"]
        validator = Draft7Validator(schema=self._meta_schema)

        if not validator.is_valid(r_schema):
            for error in sorted(validator.iter_errors(r_schema), key=str):
                if (
                    r_schema["$id"].startswith("segment/")
                    and (
                        "/identify/" in str.lower(r_schema["$id"])
                        or "/group/" in str.lower(r_schema["$id"])
                    )
                    and error.absolute_path[0] == "metadata"
                ):
                    pass  # Segment does not support metadata for identify/group calls
                else:
                    error_msg = (
                        f"Schema validation error in '{error.absolute_path[0]}' in "
                        f"{schema_path}:\n    {error.message}"
                    )
                    logger.error(error_msg)
                    errors.append(error_msg)

        # Lint event conventions
        self.lint_event_name_matches_id(
            r_schema["self"]["name"], r_schema["$id"], errors
        )
        self.lint_event_version_matches_id(
            r_schema["self"]["version"], r_schema["$id"], errors
        )
        self.lint_event_casing(r_schema["self"]["name"], r_schema["$id"], errors)
        self.lint_event_numbers(r_schema["self"]["name"], r_schema["$id"], errors)
        self.lint_event_reserved(r_schema["self"]["name"], r_schema["$id"], errors)

        # Lint property conventions
        for prop_key, prop_dict in r_schema["properties"].items():
            self.lint_property_casing(prop_key, r_schema["$id"], errors)
            self.lint_property_numbers(prop_key, r_schema["$id"], errors)
            self.lint_property_reserved(prop_key, r_schema["$id"], errors)
            self.lint_property_description(
                prop_key, prop_dict["description"], r_schema["$id"], errors
            )

            if isinstance(prop_dict["type"], str):
                prop_type_list = [prop_dict["type"]]
            else:
                prop_type_list = prop_dict["type"]

            self.lint_property_type(prop_key, prop_type_list, r_schema["$id"], errors)

        return errors
