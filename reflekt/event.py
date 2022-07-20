# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
# SPDX-License-Identifier: Apache-2.0
#
# SPDX-FileCopyrightText: 2021 Buffer
# SPDX-License-Identifier: MIT

import re
from collections import Counter

from cerberus import Validator
from loguru import logger

from reflekt.constants import CAMEL_CASE_RE, SNAKE_CASE_RE, TITLE_CASE_RE
from reflekt.project import ReflektProject
from reflekt.property import ReflektProperty
from reflekt.schema import reflekt_event_schema, reflekt_expected_metadata_schema


# The class ReflektEvent is a derivative work based on the class
# YamlEvent from project tracking-plan-kit licensed under MIT. All
# changes are licensed under Apache-2.0.
class ReflektEvent(object):
    def __init__(self, event_yaml_obj: dict) -> None:
        if ReflektProject().exists:
            self._project = ReflektProject()
            self._event_yaml_obj: dict = event_yaml_obj
            self.version: str = self._event_yaml_obj.get("version")
            self.name: str = self._event_yaml_obj.get("name")
            self.description: str = self._event_yaml_obj.get("description")
            self.metadata: dict = self._event_yaml_obj.get("metadata")
            self.properties: list = [
                ReflektProperty(property)
                for property in self._event_yaml_obj["properties"]
            ]
            self.validate_event()

    def _check_event_metadata(self) -> None:
        if self.metadata:
            validator = Validator(reflekt_expected_metadata_schema)
            is_valid: bool = validator.validate(
                self.metadata, reflekt_expected_metadata_schema
            )
            if not is_valid:
                logger.error(
                    f"Invalid event 'metadata:' config specified for event "
                    f"'{self.name}'. Error(s) summary:"
                    f"\n\n    {validator.errors}"
                    f"\n\nSee the Reflekt docs (bit.ly/reflekt-event-metadata) on "
                    f"metadata configuration."
                )
                raise SystemExit(1)

    def _check_event_name_case(self) -> None:
        case_rule: str = self._project.events_case

        if case_rule is not None:
            rule_str: str = f"case: {case_rule.lower()}"
            if case_rule.lower() == "title":
                regex: str = TITLE_CASE_RE
            elif case_rule.lower() == "snake":
                regex: str = SNAKE_CASE_RE
            elif case_rule.lower() == "camel":
                regex: str = CAMEL_CASE_RE

            match: bool = bool(re.match(regex, self.name))
            rule_type: str = "case:"
            rule_str: str = case_rule.lower()

            if not match:
                logger.error(
                    f"Event name '{self.name}' does not match naming convention"
                    f" defined by '{rule_type} {rule_str}' in reflekt_project.yml. "
                    f"See the Reflekt Project configuration docs "
                    f"(https://bit.ly/reflekt-project-config) for details on defining "
                    f"naming conventions."
                )
                raise SystemExit(1)

    def _check_event_name_numbers(self) -> None:
        allow_numbers: bool = self._project.events_allow_numbers
        if not allow_numbers:
            contains_number: bool = any(char.isdigit() for char in self.name)

            if contains_number:
                logger.error(
                    f"\nEvent name '{self.name}' does not match naming convention"
                    f" defined by 'allow_numbers: {str(allow_numbers).lower()}' in "
                    f"reflekt_project.yml See the Reflekt Project configuration docs "
                    f"(https://bit.ly/reflekt-project-config) for details on defining "
                    f"naming conventions."
                )
                raise SystemExit(1)

    def _check_duplicate_properties(self) -> None:
        if len(self.properties) == 0:
            return

        prop_names: list = [p.name for p in self.properties]
        counts = Counter(prop_names)

        duplicates: dict = {k: v for (k, v) in counts.items() if v > 1}
        if len(duplicates) > 0:
            duplicate_names: str = ", ".join(duplicates.keys())
            logger.error(
                f"Duplicate properties found on event {self.name}:\n\n"
                f"    Duplicates: {duplicate_names}"
            )
            raise SystemExit(1)

    def _check_reserved_property_names(self) -> None:
        if len(self.properties) == 0:
            return

        prop_names: list = [p.name for p in self.properties]

        for prop_name in prop_names:
            if prop_name in ReflektProject().properties_reserved:
                logger.error(
                    f"Property name '{prop_name}' is reserved and cannot be used."
                    f"See the Reflekt Project configuration docs "
                    f"(https://bit.ly/reflekt-project-config) for details on defining "
                    f"naming conventions."
                )
                raise SystemExit(1)

    def validate_event(self) -> None:
        """Validate event against Reflekt schema."""
        validator = Validator(reflekt_event_schema)
        is_valid: bool = validator.validate(self._event_yaml_obj, reflekt_event_schema)

        if not is_valid:
            logger.error(
                f"Event validation error for event '{self.name}'. Error(s) summary:"
                f"\n\n    {validator.errors}"
                f"\n\nSee the Reflekt docs (https://bit.ly/reflekt-event) for details on"
                f"defining events."
            )
            raise SystemExit(1)

        self._check_event_name_case()
        self._check_event_name_numbers()
        self._check_duplicate_properties()
        self._check_reserved_property_names()

        if reflekt_expected_metadata_schema is not None:
            self._check_event_metadata()
