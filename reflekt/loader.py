# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
# SPDX-License-Identifier: Apache-2.0
#
# SPDX-FileCopyrightText: 2021 Buffer
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import Optional
from xmlrpc.client import boolean

import yaml
from loguru import logger

from reflekt.config import ReflektConfig
from reflekt.plan import ReflektPlan
from reflekt.project import ReflektProject


# The class ReflektLoader is a derivative work based on the class
# PlanLoader from project tracking-plan-kit licensed under MIT. All
# changes are licensed under Apache-2.0.
class ReflektLoader(object):
    def __init__(
        self,
        plan_dir: Path,
        parse_all: boolean = True,
        schema_name: Optional[str] = None,
        events: Optional[tuple] = None,
        user_traits: Optional[tuple] = None,
        group_traits: Optional[tuple] = None,
    ) -> None:
        if ReflektProject().exists:
            self.config = ReflektConfig()
            self.plan_dir = plan_dir
            self.parse_all = parse_all
            self.schema_name = schema_name
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
                f"Tracking plan missing events/ directory. Events should be "
                f"defined at (one file per event): {events_path}"
            )
            raise SystemExit(1)

        glob_paths = sorted(Path(events_path).glob("**/*.yml"))

        if self.parse_all:
            events_to_parse = glob_paths
        elif self.events != () and self.events is not None:
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
        else:  # No events found. Return None
            return

        if events_to_parse != []:
            for file in events_to_parse:
                logger.info(f"    Parsing event file {file.name}")

                with open(file, "r") as event_file:
                    yaml_event_obj = yaml.safe_load(event_file)
                    for event_version in yaml_event_obj:
                        self.plan.add_event(event_version)

    def _load_user_traits(self, user_traits_path: Path) -> None:
        if self.config.plan_type == "avo":  # Avo plans have no user trait for now
            return
        elif not user_traits_path.exists():
            logger.error(
                f"Tracking plan missing user traits. User traits should be "
                f"defined in: {user_traits_path}"
            )
            raise SystemExit(1)
        elif self.parse_all or (self.user_traits != () and self.user_traits is not None):
            logger.info("    Parsing user traits file user-traits.yml")

            with open(user_traits_path, "r") as identify_file:
                yaml_obj = yaml.safe_load(identify_file)
                for trait in yaml_obj.get("traits", []):
                    self.plan.add_user_trait(trait)
        else:  # No user traits found. Return None
            return

    def _load_group_traits(self, group_traits_path) -> None:
        if self.config.plan_type == "avo":  # Avo plans have no user trait for now
            return
        elif not group_traits_path.exists():
            logger.error(
                f"Tracking plan missing group traits. Group traits should be "
                f"defined in: {group_traits_path}"
            )
            raise SystemExit(1)
        elif self.parse_all or (
            self.group_traits != () and self.group_traits is not None
        ):
            logger.info("    Parsing group traits file group-traits.yml")

            with open(group_traits_path, "r") as group_file:
                yaml_obj = yaml.safe_load(group_file)
                for trait in yaml_obj.get("traits", []):
                    self.plan.add_group_trait(trait)
