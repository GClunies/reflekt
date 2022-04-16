# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
# SPDX-License-Identifier: Apache-2.0
#
# SPDX-FileCopyrightText: 2021 Buffer
# SPDX-License-Identifier: MIT

import re
from cerberus import Validator
from collections import Counter
from reflekt.reflekt.project import ReflektProject
from reflekt.reflekt.errors import ReflektValidationError
from reflekt.reflekt.property import ReflektProperty
from reflekt.reflekt.schema import (
    reflekt_event_schema,
    reflekt_metadata_schema,
)
from reflekt.reflekt.casing import (
    TITLE_CASE_RE,
    TITLE_CASE_NUMBERS_RE,
    CAMEL_CASE_RE,
    CAMEL_CASE_NUMBERS_RE,
    SNAKE_CASE_RE,
    SNAKE_CASE_NUMBERS_RE,
)

# reserved_properties = ReflektProject().properties_reserved


# The class ReflektEvent is a derivative work based on the class
# YamlEvent from project tracking-plan-kit licensed under MIT. All
# changes are licensed under Apache-2.0.
class ReflektEvent(object):
    def __init__(self, event_yaml):
        if ReflektProject().exists:
            self._event_yaml = event_yaml
            self._properties = [
                ReflektProperty(property) for property in event_yaml["properties"]
            ]
            self.validate_event()

    @property
    def version(self):
        return self._event_yaml.get("version")

    @property
    def name(self):
        return self._event_yaml.get("name")

    @property
    def description(self):
        return self._event_yaml.get("description")

    @property
    def metadata(self):
        return self._event_yaml.get("metadata")

    @property
    def properties(self):
        return [ReflektProperty(property) for property in self._event_yaml["properties"]]

    def _check_event_metadata(self):
        if self.metadata:
            validator = Validator(reflekt_metadata_schema)
            is_valid = validator.validate(self.metadata, reflekt_metadata_schema)
            if not is_valid:
                message = (
                    f"for `metadata:` defined in event "
                    f"`{self.name}` - {validator.errors}"
                )
                raise ReflektValidationError(message)

    def _check_event_name(self):
        project = ReflektProject()
        case_rule = project.events_case
        allow_numbers = project.events_allow_numbers
        pattern_rule = project.events_pattern

        if pattern_rule is not None:
            regex = r"{}".format(pattern_rule)
            matched = re.match(regex, self.name)
            is_match = bool(matched)

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

        if is_match:
            pass
        else:
            raise ReflektValidationError(
                f"Event name '{self.name}' does not match regular "
                f"expression pattern = {pattern_rule}"
                f"\n\nEither: "
                f"\n    - Rename property to match pattern. OR;"
                f"\n    - Change `pattern:` in reflekt_project.yml."
            )

    def _check_duplicate_properties(self):
        if len(self.properties) == 0:
            return

        prop_names = [p.name for p in self.properties]
        counts = Counter(prop_names)

        duplicates = {k: v for (k, v) in counts.items() if v > 1}
        if len(duplicates) > 0:
            duplicate_names = ", ".join(duplicates.keys())
            raise ReflektValidationError(
                f"Duplicate properties found on event {self.name}. "
                f"Properties: {duplicate_names}"
            )

    def _check_reserved_property_names(self):
        if len(self.properties) == 0:
            return

        prop_names = [p.name for p in self.properties]

        for prop_name in prop_names:
            if prop_name in ReflektProject().properties_reserved:
                raise ReflektValidationError(
                    f"Property name '{prop_name}' is reserved and cannot be " f"used"
                )

    def validate_event(self):
        """Validate event against reflekt schema."""
        validator = Validator(reflekt_event_schema)
        is_valid = validator.validate(self._event_yaml, reflekt_event_schema)

        if not is_valid:
            message = f"for event `{self.name}` - {validator.errors}"
            raise ReflektValidationError(message)

        self._check_event_name()
        self._check_duplicate_properties()
        self._check_reserved_property_names()

        if reflekt_metadata_schema is not None:
            self._check_event_metadata()
