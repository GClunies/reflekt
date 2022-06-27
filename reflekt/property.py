# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
# SPDX-License-Identifier: Apache-2.0
#
# SPDX-FileCopyrightText: 2021 Buffer
# SPDX-License-Identifier: MIT

import re

from cerberus import Validator
from loguru import logger

from reflekt.constants import CAMEL_CASE_RE, SNAKE_CASE_RE, TITLE_CASE_RE
from reflekt.project import ReflektProject
from reflekt.schema import (
    reflekt_item_schema,
    reflekt_nested_property_schema,
    reflekt_property_schema,
)


# The class ReflektProperty is a derivative work based on the class
# YamlProperty from project tracking-plan-kit licensed under MIT. All
# changes are licensed under Apache-2.0.
class ReflektProperty(object):
    def __init__(self, property_yaml: dict) -> None:
        if ReflektProject().exists:
            self._project = ReflektProject()
            self._property_yaml = property_yaml
            self.name = self._property_yaml.get("name")
            self.description = self._property_yaml.get("description")
            self.type = self._property_yaml.get("type")
            self.required = self._property_yaml.get("required", False)
            self.allow_null = self._property_yaml.get("allow_null", False)
            self.enum = self._property_yaml.get("enum")
            self.pattern = self._property_yaml.get("pattern")
            self.datetime = self._property_yaml.get("datetime")
            self.array_item_schema = self._property_yaml.get("array_item_schema")
            self.object_properties = self._property_yaml.get("object_properties")
            self.validate_property()

    def _check_description(self) -> None:
        if self.description == "":
            logger.error(f"Property {self.name} has no description.")
            raise SystemExit(1)

    def _check_enum(self) -> None:
        if self.type != "string" and self.enum:
            logger.error(
                f"Property {self.name} is of type {self.type}. Cannot specify "
                f"'enum:' for {self.type} data type, only for string data type."
            )
            raise SystemExit(1)

    def _check_pattern(self) -> None:
        if self.type != "string" and self.pattern:
            logger.error(
                f"Property {self.name} is of type {self.type}. Cannot specify "
                f"'pattern:' for {self.type} data type, only for string data type."
            )
            raise SystemExit(1)

    def _check_datetime(self) -> None:
        if self.type != "string" and self.datetime:
            logger.error(
                f"Property {self.name} is of type {self.type}. Cannot specify "
                f"'datetime:' for {self.type} data type, only for string data type."
            )
            raise SystemExit(1)

    def _check_array_item_schema(self) -> None:
        if self.array_item_schema:
            for array_item in self.array_item_schema:
                validator = Validator(reflekt_item_schema)
                is_valid = validator.validate(array_item, reflekt_item_schema)

                if not is_valid:
                    logger.error(
                        f"Validation error detected for nested array property "
                        f"'{array_item['name']}' (parent property = {self.name})."
                        f"Errors:"
                        f"\n\n    {validator.errors}"
                    )
                    raise SystemExit(1)

        if self.type != "array" and self.array_item_schema:
            logger.error(
                f"Property {self.name} is of type {self.type}. Cannot specify "
                f"'array_item_schema:' for {self.type} data type. "
                f"Only for array data type."
            )
            raise SystemExit(1)

    def _check_object_properties(self) -> None:
        if self.object_properties:
            for object_property in self.object_properties:
                validator = Validator(reflekt_nested_property_schema)
                is_valid = validator.validate(
                    object_property, reflekt_nested_property_schema
                )

                if not is_valid:
                    logger.error(
                        f"Validation error detected for object property "
                        f"'{object_property['name']}' (parent property = {self.name})."
                        f"Errors:"
                        f"\n\n    {validator.errors}"
                    )
                    raise SystemExit(1)

        if self.type != "object" and self.object_properties:
            logger.error(
                f"Property {self.name} is of type {self.type}. Cannot specify "
                f"'object_properties:' for {self.type} data type. "
                f"Only for object data type."
            )
            raise SystemExit(1)

    def _check_property_name_case(self) -> None:
        case_rule = self._project.properties_case

        if case_rule is not None:
            rule_str = f"case: {case_rule.lower()}"
            if case_rule.lower() == "title":
                regex = TITLE_CASE_RE
            elif case_rule.lower() == "snake":
                regex = SNAKE_CASE_RE
            elif case_rule.lower() == "camel":
                regex = CAMEL_CASE_RE

            match = bool(re.match(regex, self.name))
            rule_type = "case:"
            rule_str = case_rule.lower()

            if not match:
                logger.error(
                    f"Property name '{self.name}' does not match naming convention "
                    f"defined by '{rule_type} {rule_str}' in reflekt_project.yml."
                    f"\n\nEither: "
                    f"\n    - Rename property to match config."
                    f"\n    - Change '{rule_type} {rule_str}' in reflekt_project.yml."
                )
                raise SystemExit(1)

    def _check_property_name_numbers(self) -> None:
        allow_numbers = self._project.properties_allow_numbers
        if not allow_numbers:
            contains_number = any(char.isdigit() for char in self.name)

            if contains_number:
                logger.error(
                    f"Property name '{self.name}' does not match naming convention"
                    f" defined by 'allow_numbers: {str(allow_numbers).lower()}' in reflekt_project.yml "  # noqa: E501
                    f"\n\nEither: "
                    f"\n    - Rename property to match config. OR;"
                    f"\n    - Change 'allow_numbers:' rule for events in reflekt_project.yml."  # noqa: E501
                )
                raise SystemExit(1)

    def validate_property(self) -> None:
        """Validate event property against Reflekt schema."""
        validator = Validator(reflekt_property_schema)
        is_valid = validator.validate(self._property_yaml, reflekt_property_schema)

        if not is_valid:
            logger.error(
                f"Validation error detected for property '{self.name}'. Errors:"
                f"\n\n    {validator.errors}"
            )
            raise SystemExit(1)

        self._check_property_name_case()
        self._check_property_name_numbers()
        self._check_description()
        self._check_enum()
        self._check_pattern()
        self._check_datetime()
        self._check_array_item_schema()
        self._check_object_properties()
