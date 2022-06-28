# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
# SPDX-License-Identifier: Apache-2.0
#
# SPDX-FileCopyrightText: 2021 Buffer
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import Optional

import yaml
from loguru import logger

from reflekt.plan import ReflektPlan
from reflekt.project import ReflektProject


# The class ReflektLoader is a derivative work based on the class
# PlanLoader from project tracking-plan-kit licensed under MIT. All
# changes are licensed under Apache-2.0.
class ReflektLoader(object):
    def __init__(
        self,
        plan_dir: Path,
        plan_name: str,
        schema_name: Optional[str] = None,
        events: Optional[tuple] = None,
    ) -> None:
        # self._validation_errors = []
        if ReflektProject().exists:
            self.plan_name = plan_name
            self.schema_name = schema_name
            self.plan_dir = plan_dir
            self._load_plan_file(plan_dir / "plan.yml")
            self._load_events(plan_dir / "events", events)
            self._load_identify_traits(plan_dir / "user-traits.yml")
            self._load_group_traits(plan_dir / "group-traits.yml")
            self.plan.validate_plan()

    def _load_plan_file(self, path: Path) -> None:
        with open(path, "r") as plan_file:
            yaml_obj = yaml.safe_load(plan_file)
            self.plan = ReflektPlan(
                plan_yaml_obj=yaml_obj,
                plan_name=self.plan_name,
                schema_name=self.schema_name,
            )

    def _load_events(self, path: Path, events: Optional[tuple] = None) -> None:
        glob_paths = sorted(Path(path).glob("**/*.yml"))

        if events != () and events is not None:
            event_paths = []
            for event in events:
                event_paths.append(self.plan_dir / "events" / f"{event}.yml")
                events_to_parse = []
                for event_path in event_paths:
                    if event_path not in glob_paths:
                        logger.error(
                            f"Event '{event}' not found in tracking plan "
                            f"{self.plan_name}."
                        )
                        raise SystemExit(1)

                    events_to_parse.append(event_path)

        else:
            events_to_parse = glob_paths

        for file in events_to_parse:
            logger.info(
                f"    Parsing event file {file.name}",
            )

            with open(file, "r") as event_file:
                yaml_event_obj = yaml.safe_load(event_file)
                for event_version in yaml_event_obj:
                    self.plan.add_event(event_version)

    def _load_identify_traits(self, path: Path) -> None:
        if not path.exists():
            return

        with open(path, "r") as identify_file:
            yaml_obj = yaml.safe_load(identify_file)
            for trait in yaml_obj.get("traits", []):
                self.plan.add_identify_trait(trait)

    def _load_group_traits(self, path) -> None:
        if not path.exists():
            return

        with open(path, "r") as group_file:
            yaml_obj = yaml.safe_load(group_file)
            for trait in yaml_obj.get("traits", []):
                self.plan.add_group_trait(trait)
