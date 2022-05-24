# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
# SPDX-License-Identifier: Apache-2.0
#
# SPDX-FileCopyrightText: 2021 Buffer
# SPDX-License-Identifier: MIT

import re
from typing import Optional

from cerberus import Validator

from reflekt.reflekt.casing import (
    CAMEL_CASE_NUMBERS_RE,
    CAMEL_CASE_RE,
    SNAKE_CASE_NUMBERS_RE,
    SNAKE_CASE_RE,
    TITLE_CASE_NUMBERS_RE,
    TITLE_CASE_RE,
)
from reflekt.reflekt.errors import ReflektValidationError
from reflekt.reflekt.project import ReflektProject
from reflekt.reflekt.schema import (
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
            self._property_yaml = property_yaml
            self.validate_property()

    @property
    def name(self) -> str:
        return self._property_yaml.get("name")

    @property
    def description(self) -> str:
        return self._property_yaml.get("description")

    @property
    def type(self) -> str:
        return self._property_yaml.get("type")

    @property
    def required(self) -> bool:
        return self._property_yaml.get("required", False)

    @property
    def allow_null(self) -> bool:
        return self._property_yaml.get("allow_null", False)

    @property
    def enum(self) -> str:
        return self._property_yaml.get("enum")

    @property
    def datetime(self) -> Optional[bool]:
        return self._property_yaml.get("datetime")

    @property
    def array_item_schema(self) -> Optional[dict]:
        return self._property_yaml.get("array_item_schema")

    @property
    def object_properties(self) -> Optional[dict]:
        return self._property_yaml.get("object_properties")

    def _check_description(self) -> None:
        if self.description == "":
            message = f"Property {self.name} has no description."
            raise ReflektValidationError(message)

    def _check_enum(self) -> None:
        if self.type != "string" and self.enum:
            message = (
                f"Property {self.name} is of type {self.type}. Cannot specify "
                f"`enum:` for {self.type} data types. "
                f"Only for string data types"
            )
            raise ReflektValidationError(message)

    def _check_datetime(self) -> None:
        if self.type != "string" and self.datetime:
            message = (
                f"Property {self.name} is of type {self.type}. Cannot specify "
                f"`datetime:` for {self.type} data types. "
                f"Only for string data types"
            )
            raise ReflektValidationError(message)

    def _check_array_item_schema(self) -> None:
        if self.array_item_schema:
            for array_item in self.array_item_schema:
                validator = Validator(reflekt_item_schema)
                is_valid = validator.validate(array_item, reflekt_item_schema)

                if not is_valid:
                    message = (
                        f"for {array_item['name']} defined in property "
                        f"{self.name} - {validator.errors}"
                    )
                    raise ReflektValidationError(message)

        if self.type != "array" and self.array_item_schema:
            if self.type is None:
                print(self._property_yaml)
            message = (
                f"Property {self.name} is of type {self.type}. Cannot specify "
                f"`array_item_schema:` for {self.type} data types. "
                f"Only for array data types"
            )
            raise ReflektValidationError(message)

    def _check_object_properties(self) -> None:
        if self.object_properties:
            for object_property in self.object_properties:
                validator = Validator(reflekt_nested_property_schema)
                is_valid = validator.validate(
                    object_property, reflekt_nested_property_schema
                )

                if not is_valid:
                    message = (
                        f"object property "
                        f"{object_property['name']} - {validator.errors}. "
                        f"Parent property is {self.name}."
                    )
                    raise ReflektValidationError(message)

        if self.type != "object" and self.object_properties:
            message = (
                f"Property {self.name} is of type {self.type}. Cannot specify "
                f"object_properties for {self.type} data types. "
                f"Only for object data types"
            )
            raise ReflektValidationError(message)

    def _check_property_name(self) -> None:
        project = ReflektProject()
        case_rule = project.properties_case
        allow_numbers = project.properties_allow_numbers

        if case_rule is not None:
            if case_rule.lower() == "title":
                if allow_numbers:
                    regex = TITLE_CASE_NUMBERS_RE
                else:
                    regex = TITLE_CASE_RE

            if case_rule.lower() == "snake":
                if allow_numbers:
                    regex = SNAKE_CASE_NUMBERS_RE
                else:
                    regex = SNAKE_CASE_RE

            if case_rule.lower() == "camel":
                if allow_numbers:
                    regex = CAMEL_CASE_NUMBERS_RE
                else:
                    regex = CAMEL_CASE_RE

            matched = re.match(regex, self.name)
            is_match = bool(matched)
            rule_type = "case:"
            rule_str = case_rule.lower()

        if is_match:
            pass
        else:
            raise ReflektValidationError(
                f"Property name '{self.name}' does not match naming convention"
                f" defined by '{rule_type} {rule_str}' in reflekt_project.yml "
                f"\n\nEither: "
                f"\n    - Rename property to match config. OR;"
                f"\n    - Change '{rule_type} {rule_str}' in reflekt_project.yml."
            )

    def validate_property(self) -> None:
        """Validate event property against Reflekt schema."""
        validator = Validator(reflekt_property_schema)
        is_valid = validator.validate(self._property_yaml, reflekt_property_schema)

        if not is_valid:
            message = f"for property '{self.name}' - {validator.errors}"
            raise ReflektValidationError(message)

        self._check_property_name()
        self._check_description()
        self._check_enum()
        self._check_datetime()
        self._check_array_item_schema()
        self._check_object_properties()
