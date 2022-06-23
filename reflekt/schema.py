# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from reflekt.project import ReflektProject

# fmt: off
reflekt_plan_schema = {
    "name": {"required": True, "type": "string"},
    "dbt_pkg_schema": {"required": False, "type": "string"},
}

reflekt_event_schema = {
    "version": {"required": True, "type": "integer", "min": 1},
    "name": {"required": True, "type": "string"},
    "description": {"required": True, "type": "string"},
    "metadata": {"required": False, "type": "dict"},
    "properties": {"required": True, "type": "list"},
}

reflekt_project = ReflektProject()

if reflekt_project.exists:
    reflekt_property_schema = {
        "name": {"required": True, "type": "string"},
        "description": {"required": True, "type": "string"},
        "type": {
            "required": True,
            "allowed": reflekt_project.data_types,
        },
        "allow_null": {"required": False, "type": "boolean"},
        "required": {"required": False, "type": "boolean"},
        "enum": {"required": False, "type": "list"},
        "pattern": {"required": False, "type": "string"},
        "datetime": {"required": False, "type": "boolean"},
        "object_properties": {"required": False, "type": "list"},
        "array_item_schema": {"required": False, "type": "list"},
    }

    reflekt_item_schema = {
        "name": {"required": True, "type": "string"},
        "description": {"required": True, "type": "string"},
        "type": {
            "required": True,
            "allowed": reflekt_project.data_types,
        },
        "allow_null": {"required": False, "type": "boolean"},
        "required": {"required": False, "type": "boolean"},
        "enum": {"required": False, "type": "list"},
        "pattern": {"required": False, "type": "string"},
        "datetime": {"required": False, "type": "boolean"},
    }

    reflekt_nested_property_schema = {
        "name": {"required": True, "type": "string"},
        "description": {"required": True, "type": "string"},
        "type": {
            "required": True,
            "allowed": reflekt_project.data_types,
        },
        "allow_null": {"required": False, "type": "boolean"},
        "required": {"required": False, "type": "boolean"},
        "enum": {"required": False, "type": "list"},
        "pattern": {"required": False, "type": "string"},
        "datetime": {"required": False, "type": "boolean"},
    }

    if reflekt_project.expected_metadata_schema is not None:
        reflekt_expected_metadata_schema = reflekt_project.expected_metadata_schema

    else:
        reflekt_expected_metadata_schema = None

else:  # These are just dummy objects to prevent import side-effects
    reflekt_expected_metadata_schema = {}
    reflekt_property_schema = {}
    reflekt_item_schema = {}
    reflekt_nested_property_schema = {}
