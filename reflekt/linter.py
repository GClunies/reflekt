# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json

from jsonschema import ValidationError, validate
from loguru import logger

from reflekt.casing import event_case, property_case
from reflekt.errors import LintingError
from reflekt.project import Project


project = Project()
schema_path = project.dir / "schemas/.reflekt/event-meta/1-0.json"

with schema_path.open() as f:
    schema = json.load(f)


def lint_event_casing(event_name: str, schema_path: str):
    """Check that the event name is in the correct casing.

    Args:
        event_name (str): The event name.
        schema_path (str): The schema path.

    Raises:
        LintingError: Raised when the event name is not in the correct casing.
    """
    if event_name != event_case(event_name):
        err_msg = (
            f"Event '{event_name}' in {schema_path} does not match naming convention "
            f"'casing: {project.conventions['event']['casing']}') in {project.path}. "
            f"Event name should be '{event_case(event_name)}'"
        )
        logger.error(err_msg)
        raise LintingError(message=err_msg)


def lint_event_numbers(event_name: str, schema_path: str):
    """Check that the event name does not contain numbers.

    Args:
        event_name (str): The event name.
        schema_path (str): The schema path.

    Raises:
        LintingError: Raised when the event name contains numbers.
    """
    if any(char.isdigit() for char in event_name):
        err_msg = (
            f"Event '{event_name}' in {schema_path} does not match naming convention "
            f"'numbers: {project.conventions['event']['numbers']}') in {project.path}. "
            f"Event name should be '{event_case(event_name)}'"
        )
        logger.error(err_msg)
        raise LintingError(message=err_msg)


def lint_event_reserved(event_name: str, schema_path: str):
    """Check that the event name is not a reserved name.

    Args:
        event_name (str): The event name.
        schema_path (str): The schema path.

    Raises:
        LintingError: Raised when the event name contains reserved words.
    """
    if event_name in project.conventions["event"]["reserved"]:
        err_msg = (
            f"Event '{event_name}' in {schema_path} is a reserved name in convention "
            f"in {project.path}. Reserved event names are:\n"
            f"    'reserved: {project.conventions['event']['reserved']}')"
        )
        logger.error(err_msg)
        raise LintingError(message=err_msg)


def lint_property_casing(prop_name: str, schema_path: str):
    """Check that the property name is in the correct casing.

    Args:
        prop_name (str): The property name.
        schema_path (str): The schema path.

    Raises:
        LintingError: Raised when the property name is not in the correct casing.
    """
    if prop_name != property_case(prop_name):
        err_msg = (
            f"Property '{prop_name}' in {schema_path} does not match naming convention "
            f"'casing: {project.conventions['property']['casing']}') in {project.path}."
            f" Property name should be '{property_case(prop_name)}'"
        )
        logger.error(err_msg)
        raise LintingError(message=err_msg)


def lint_property_numbers(prop_name: str, schema_path: str):
    """Check that the property name does not contain numbers.

    Args:
        prop_name (str): The property name.
        schema_path (str): The schema path.

    Raises:
        LintingError: Raised when the property name contains numbers.
    """
    if any(char.isdigit() for char in prop_name):
        err_msg = (
            f"Property '{prop_name}' in {schema_path} does not match naming convention "
            f"'numbers: {project.conventions['property']['numbers']}') in "
            f"{project.path}. Property name should be '{property_case(prop_name)}'"
        )
        logger.error(err_msg)
        raise LintingError(message=err_msg)


def lint_property_reserved(prop_name: str, schema_path: str):
    """Check that the property name is not a reserved name.

    Args:
        prop_name (str): The property name.
        schema_path (str): The schema path.

    Raises:
        LintingError: Raised when the property name contains reserved words.
    """
    if prop_name in project.conventions["property"]["reserved"]:
        err_msg = (
            f"Property '{prop_name}' in {schema_path} is a reserved name in "
            f"{project.path}. Reserved property names are:\n"
            f"    'reserved: {project.conventions['property']['reserved']}')"
        )
        logger.error(err_msg)
        raise LintingError(message=err_msg)


def lint_property_description(prop_name: str, description: str, schema_path: str):
    """Check that the property description is not empty.

    Args:
        prop_name (str): The property name.
        description (str): The property description.
        schema_path (str): The schema path.

    Raises:
        LintingError: Raised when the property description is empty.
    """
    if not description:
        raise LintingError(
            message=(
                f"Property '{prop_name}' in schema '{schema_path}' has an empty "
                f"description."
            )
        )


def lint_property_type(prop_name: str, prop_type_list: list, schema_path: str):
    """Check that the property data type is valid.

    Args:
        prop_name (str): The property name.
        prop_type_list (list): List of valid property data types.
        schema_path (str): The schema path.

    Raises:
        LintingError: Raised when the property type is empty.
    """
    for prop_type in prop_type_list:
        if prop_type not in project.conventions["data_types"]:
            raise LintingError(
                message=(
                    f"Property '{prop_name}' in schema '{schema_path}' has type "
                    f"'{prop_type}' which is not allowed per configuration: "
                    f"{project.conventions['data_types']} in reflekt_project.yml."
                )
            )


def lint_schema(r_schema: dict, errors: list):
    """Lint event schema.

    Linting is performed against conventions defined in reflekt_project.yml and
    schemas/.reflekt/event-meta/1-0.json.

    Args:
        r_schema (dict): The schema to lint.
        errors (list): A list of errors to append to if any errors are found.
    """
    schema_path = project.dir / "schemas" / r_schema["$id"]

    try:
        validate(r_schema, schema)
    except ValidationError as e:
        if (
            "segment" in r_schema["$id"]
            and (
                "/identify/" in str.lower(r_schema["$id"])
                or "/group/" in str.lower(r_schema["$id"])
            )
            and e.absolute_path[0] == "metadata"
        ):
            pass  # Identify and Group Segment schemas do not have metadata
        else:
            fail_param = e.absolute_path[0]
            err_msg = (
                f"Schema validation error in '{fail_param}' in {schema_path}:\n"
                f"  {e.message}"
            )
            logger.error(err_msg)
            errors.append(e.message)

    # Lint event conventions
    try:
        lint_event_casing(r_schema["self"]["name"], r_schema["$id"])
        lint_event_numbers(r_schema["self"]["name"], r_schema["$id"])
        lint_event_reserved(r_schema["self"]["name"], r_schema["$id"])
    except LintingError as e:
        errors.append(e.message)

    for prop_key, prop_dict in r_schema["properties"].items():
        try:
            lint_property_casing(prop_key, r_schema["$id"])
            lint_property_numbers(prop_key, r_schema["$id"])
            lint_property_reserved(prop_key, r_schema["$id"])
            lint_property_description(
                prop_key, prop_dict["description"], r_schema["$id"]
            )
            if isinstance(prop_dict["type"], str):
                prop_type_list = [prop_dict["type"]]
            else:
                prop_type_list = prop_dict["type"]

            lint_property_type(prop_key, prop_type_list, r_schema["$id"])

        except LintingError as e:
            errors.append(e.message)
