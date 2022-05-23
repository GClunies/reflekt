# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
# SPDX-License-Identifier: Apache-2.0
#
# SPDX-FileCopyrightText: 2021 Buffer
# SPDX-License-Identifier: MIT

from typing import Counter

from cerberus import Validator

from reflekt.reflekt.config import ReflektConfig
from reflekt.reflekt.errors import ReflektValidationError
from reflekt.reflekt.event import ReflektEvent
from reflekt.reflekt.project import ReflektProject
from reflekt.reflekt.property import ReflektProperty
from reflekt.reflekt.schema import reflekt_plan_schema


# The class ReflektPlan is a derivative work based on the class
# YamlTrackingPlan from project tracking-plan-kit licensed under MIT. All
# changes are licensed under Apache-2.0.
class ReflektPlan(object):
    def __init__(self, plan_yaml_obj, plan_name):
        if ReflektProject().exists:
            self._config = ReflektConfig()
            self._project = ReflektProject()
            self.plan_yaml_obj = plan_yaml_obj
            self.name = plan_name
            self.plan_schemas = self._get_plan_schemas(self.name)
            self.dbt_package_schema = self._get_dbt_package_schema()
            self.events = []
            self.identify_traits = []
            self.group_traits = []

    def _get_plan_schemas(self, plan_name):
        try:
            plan_schemas = self._project.plan_schemas[plan_name]
        except KeyError:
            raise KeyError(
                f"Tracking plan '{plan_name}' not found in "
                f"`plan_db_schemas:` in reflekt_project.yml. Please add "
                f"corresponding '{plan_name}: <schema>` key value pair."
            )

        return plan_schemas

    def _get_dbt_package_schema(self):
        if self._project.pkg_schemas is not None:
            if self.name in self._project.pkg_schemas:
                return self._project.pkg_schemas[self.name]
        else:
            return None

    def add_event(self, event_yaml_obj):
        event = ReflektEvent(event_yaml_obj)
        self.events.append(event)

    def add_identify_trait(self, trait_yaml):
        trait_property = ReflektProperty(trait_yaml)
        self.identify_traits.append(trait_property)

    def add_group_trait(self, trait_yaml):
        trait_property = ReflektProperty(trait_yaml)
        self.group_traits.append(trait_property)

    def _check_duplicate_events(self):
        event_ids = map(lambda e: e.name + str(e.version), self.events)
        counts = Counter(event_ids)
        duplicates = {k: v for (k, v) in counts.items() if v > 1}

        if len(duplicates) > 0:
            duplicate_names = ", ".join(duplicates.keys())
            raise ReflektValidationError(
                f"Duplicate events found. Events: {duplicate_names}"
            )

    def _check_reserved_event_names(self):
        if len(self.events) == 0:
            return

        event_names = [e.name for e in self.events]

        for event_name in event_names:
            if event_name in ReflektProject().events_reserved:
                raise ReflektValidationError(
                    f"Event name '{event_name}' is reserved and cannot be " f"used."
                )

    def validate_plan(self):
        validator = Validator(reflekt_plan_schema)
        is_valid = validator.validate(self.plan_yaml_obj, reflekt_plan_schema)

        if not is_valid:
            message = f"For plan '{self.name}' - {validator.errors}"
            raise ReflektValidationError(message)

        self._check_duplicate_events()
        self._check_reserved_event_names()
