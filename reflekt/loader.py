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
        schema_name: Optional[str] = None,
        events: Optional[tuple] = None,
        user_traits: Optional[tuple] = None,
        group_traits: Optional[tuple] = None,
    ) -> None:
        if ReflektProject().exists:
            self.schema_name = schema_name
            self.plan_dir = plan_dir
            self.events = events
            self.user_traits = user_traits
            self.group_traits = group_traits

            self._load_plan_file(plan_dir / "plan.yml")
            self._load_events(plan_dir / "events")
            self._load_user_traits(plan_dir / "user-traits.yml")
            self._load_group_traits(plan_dir / "group-traits.yml")
            self.plan.validate_plan()

    def _load_plan_file(self, plan_path: Path) -> None:
        if not plan_path.exists():
            logger.error(f"Tracking plan missing plan file. Should be at: {plan_path}")

        with open(plan_path, "r") as plan_file:
            yaml_obj = yaml.safe_load(plan_file)
            self.plan_name = yaml_obj["name"]  # Set plan name from plan.yml
            self.plan = ReflektPlan(
                plan_yaml_obj=yaml_obj,
                plan_name=self.plan_name,
                schema_name=self.schema_name,
            )

    def _load_events(self, events_path: Path) -> None:
        if not events_path.exists():
            logger.error(
                f"Tracking plan missing events. Events should be "
                f"defined at (one file per event): {events_path}"
            )
            raise SystemExit(1)

        if self.events == ():
            return

        glob_paths = sorted(Path(events_path).glob("**/*.yml"))

        if self.events != () and self.events is not None:
            event_paths = []

            for event in self.events:
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
            logger.info(f"    Parsing event file {file.name}")

            with open(file, "r") as event_file:
                yaml_event_obj = yaml.safe_load(event_file)
                for event_version in yaml_event_obj:
                    self.plan.add_event(event_version)

    def _load_user_traits(self, user_traits_path: Path) -> None:
        if not user_traits_path.exists():
            logger.error(
                f"Tracking plan missing user traits. User traits should be "
                f"defined in: {user_traits_path}"
            )
            raise SystemExit(1)

        if self.user_traits == ():
            return

        parse_user_traits = True

        if self.user_traits != () and self.user_traits is not None:
            if "user-traits" not in self.user_traits:
                parse_user_traits = False

        if parse_user_traits:
            logger.info("    Parsing user traits file user-traits.yml")

            with open(user_traits_path, "r") as identify_file:
                yaml_obj = yaml.safe_load(identify_file)
                for trait in yaml_obj.get("traits", []):
                    self.plan.add_user_trait(trait)

    def _load_group_traits(self, group_traits_path) -> None:
        if not group_traits_path.exists():
            logger.error(
                f"Tracking plan missing group traits. Group traits should be "
                f"defined in: {group_traits_path}"
            )
            raise SystemExit(1)

        if self.group_traits == ():
            return

        parse_group_traits = True

        if self.group_traits != () and self.group_traits is not None:
            if "group-traits" not in self.group_traits:
                parse_group_traits = False

        if parse_group_traits:
            logger.info("    Parsing group traits file group-traits.yml")

            with open(group_traits_path, "r") as group_file:
                yaml_obj = yaml.safe_load(group_file)
                for trait in yaml_obj.get("traits", []):
                    self.plan.add_group_trait(trait)
