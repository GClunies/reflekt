# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
# SPDX-License-Identifier: Apache-2.0
#
# SPDX-FileCopyrightText: 2021 Buffer
# SPDX-License-Identifier: MIT

from typing import Counter, List, Optional

from cerberus import Validator

from reflekt.reflekt.config import ReflektConfig
from reflekt.reflekt.errors import ReflektValidationError
from reflekt.reflekt.event import ReflektEvent
from reflekt.reflekt.project import ReflektProject
from reflekt.reflekt.property import ReflektProperty
from reflekt.reflekt.schema import reflekt_plan_schema
from reflekt.reflekt.trait import ReflektTrait


# The class ReflektPlan is a derivative work based on the class
# YamlTrackingPlan from project tracking-plan-kit licensed under MIT. All
# changes are licensed under Apache-2.0.
class ReflektPlan(object):
    def __init__(
        self,
        plan_yaml_obj: dict,
        plan_name: str,
        schema_name: Optional[str] = None,
    ) -> None:
        if ReflektProject().exists:
            self._config = ReflektConfig()
            self._project = ReflektProject()
            self.plan_yaml_obj = plan_yaml_obj
            self.name = plan_name

            if schema_name:
                self.schema_arg = schema_name
                self.database = self._get_database(self.name)
                self.schema, self.schema_alias = self._get_schema_and_schema_alias(
                    self.name
                )
            else:
                self.database = None
                self.schema = None
                self.schema_alias = None

            self.events: List[ReflektEvent] = []
            self.identify_traits: List[ReflektTrait] = []
            self.group_traits: List[ReflektTrait] = []

    def _get_database(self, plan_name: str) -> list:
        try:
            plan_database = self._project.warehouse_database_obj[plan_name]
            return plan_database
        except KeyError:
            raise KeyError(
                f"Tracking plan '{plan_name}' not found under...\n\n"
                f"    warehouse:\n"
                f"      database:\n\n"
                f"... in reflekt_project.yml. See docs in Reflekt GitHub repo "
                f"(https://github.com/GClunies/reflekt) on how to specify."
            )

    def _get_schema_and_schema_alias(self, plan_name: str) -> list:
        try:
            schema_configs = self._project.warehouse_schema_obj[plan_name]

            for schema_config in schema_configs:
                if schema_config["schema"] == self.schema_arg:
                    schema = schema_config["schema"]
                    schema_alias = schema_config.get("schema_alias")

                    return schema, schema_alias

        except KeyError:
            raise KeyError(
                f"Error in 'schema:' config for tracking plan '{plan_name}'."
                f"See Reflekt docs for guidance on 'schema:' config.\n"
                f"    https://github.com/GClunies/reflekt/blob/main/docs/DOCUMENTATION.md/#reflekt-project"  # noqa: E501
            )

    def add_event(self, event_yaml_obj: dict) -> None:
        self.events.append(ReflektEvent(event_yaml_obj))

    def add_identify_trait(self, trait_yaml: dict) -> None:
        trait_property = ReflektProperty(trait_yaml)
        self.identify_traits.append(trait_property)

    def add_group_trait(self, trait_yaml: dict) -> None:
        trait_property = ReflektProperty(trait_yaml)
        self.group_traits.append(trait_property)

    def _check_duplicate_events(self) -> None:
        event_ids = map(lambda e: e.name + str(e.version), self.events)
        counts = Counter(event_ids)
        duplicates = {k: v for (k, v) in counts.items() if v > 1}

        if len(duplicates) > 0:
            duplicate_names = ", ".join(duplicates.keys())
            raise ReflektValidationError(
                f"Duplicate events found. Events: {duplicate_names}"
            )

    def _check_reserved_event_names(self) -> None:
        if len(self.events) == 0:
            return

        event_names = [e.name for e in self.events]

        for event_name in event_names:
            if event_name in ReflektProject().events_reserved:
                raise ReflektValidationError(
                    f"Event name '{event_name}' is reserved and cannot be " f"used."
                )

    def validate_plan(self) -> None:
        validator = Validator(reflekt_plan_schema)
        is_valid = validator.validate(self.plan_yaml_obj, reflekt_plan_schema)

        if not is_valid:
            message = f"For plan '{self.name}' - {validator.errors}"
            raise ReflektValidationError(message)

        self._check_duplicate_events()
        self._check_reserved_event_names()
