# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
# SPDX-License-Identifier: Apache-2.0
#
# SPDX-FileCopyrightText: 2021 Buffer
# SPDX-License-Identifier: MIT

from typing import Counter

from cerberus import Validator

from reflekt.reflekt.errors import ReflektValidationError
from reflekt.reflekt.event import ReflektEvent
from reflekt.reflekt.project import ReflektProject
from reflekt.reflekt.property import ReflektProperty
from reflekt.reflekt.schema import reflekt_plan_schema


# The class ReflektPlan is a derivative work based on the class
# YamlTrackingPlan from project tracking-plan-kit licensed under MIT. All
# changes are licensed under Apache-2.0.
class ReflektPlan(object):
    def __init__(self, plan_yaml):
        if ReflektProject().exists:
            self._plan_yaml = plan_yaml
            self._events = []
            self._identify_traits = []
            self._group_traits = []
            self.validate_plan()

    @classmethod
    def from_yaml(cls, plan_yaml):
        return cls(plan_yaml)

    @property
    def name(self):
        return self._plan_yaml.get("name")

    @property
    def events(self):
        return self._events

    @property
    def identify_traits(self):
        return self._identify_traits

    @property
    def group_traits(self):
        return self._group_traits

    def add_event(self, event_yaml):
        event = ReflektEvent(event_yaml)
        self._events.append(event)

    def add_identify_trait(self, trait_yaml):
        trait_property = ReflektProperty(trait_yaml)
        self._identify_traits.append(trait_property)

    def add_group_trait(self, trait_yaml):
        trait_property = ReflektProperty(trait_yaml)
        self._group_traits.append(trait_property)

    def _check_duplicate_events(self):
        event_ids = map(lambda e: e.name + str(e.version), self._events)
        counts = Counter(event_ids)
        duplicates = {k: v for (k, v) in counts.items() if v > 1}

        if len(duplicates) > 0:
            duplicate_names = ", ".join(duplicates.keys())
            raise ReflektValidationError(
                f"Duplicate events found. Events: {duplicate_names}"
            )

    def _check_reserved_event_names(self):
        if len(self._events) == 0:
            return

        event_names = [e.name for e in self._events]

        for event_name in event_names:
            if event_name in ReflektProject().events_reserved:
                raise ReflektValidationError(
                    f"Event name '{event_name}' is reserved and cannot be " f"used."
                )

    def validate_plan(self):
        validator = Validator(reflekt_plan_schema)
        is_valid = validator.validate(self._plan_yaml, reflekt_plan_schema)

        if not is_valid:
            message = f"For plan `{self.display_name}` - {validator.errors}"
            raise ReflektValidationError(message)

        self._check_duplicate_events()
        self._check_reserved_event_names()
