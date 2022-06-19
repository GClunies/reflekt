# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
# SPDX-License-Identifier: Apache-2.0
#
# SPDX-FileCopyrightText: 2021 Buffer
# SPDX-License-Identifier: MIT

import json
import shutil
from pathlib import Path

import funcy
import yaml
from inflection import dasherize, underscore
from loguru import logger

from reflekt.dumper import ReflektYamlDumper
from reflekt.segment.parser import parse_segment_event, parse_segment_property


# The class SegmentPlan is a derivative work based on the class
# JsonTrackingPlan from project tracking-plan-kit licensed under MIT. All
# changes are licensed under Apache-2.0.
class SegmentPlan(object):
    def __init__(self, plan_json: dict):
        self.plan_json = plan_json

    @classmethod
    def parse_string(cls, json_string: str):
        parsed_json = json.loads(json_string)
        plan = cls(parsed_json)
        return plan

    @classmethod
    def parse_file(cls, json_file_path: Path):
        with open(json_file_path, "r") as f:
            contents = f.read()
        return cls.parse_string(contents)

    @property
    def display_name(self):
        return self.plan_json.get("display_name")

    @property
    def name(self):
        return self.plan_json.get("name")

    def build_reflekt(self, plan_dir: Path):
        events_dir = plan_dir / "events"
        # Always start from a clean Reflekt plan
        if plan_dir.is_dir():
            shutil.rmtree(plan_dir)
        for dir in [plan_dir, events_dir]:
            if not dir.exists():
                dir.mkdir()

        self._build_reflekt_plan_file(plan_dir)
        traits_json = (
            self.plan_json.get("rules")
            .get("identify", {})
            .get("properties", {})
            .get("traits", {})
            .get("properties")
        )

        if traits_json:
            logger.info("    Writing Reflekt identify traits to identify.yml")
            self._build_reflekt_identify_file(plan_dir, traits_json)

        group_traits_json = (
            self.plan_json.get("rules")
            .get("group", {})
            .get("properties", {})
            .get("traits", {})
            .get("properties")
        )

        if group_traits_json:
            logger.info("   Writing Reflekt group traits to group.yml")
            self._build_reflekt_group_file(plan_dir, group_traits_json)

        for event_json in self.plan_json.get("rules", {}).get("events", []):
            self._build_reflekt_event_file(events_dir, event_json)

    def _build_reflekt_plan_file(self, plan_dir: Path):
        plan_file = plan_dir / "plan.yml"
        plan_obj = {
            "name": self.display_name
        }  # Segment refers to the plan name as the `display_name` in their API

        with open(plan_file, "w") as f:
            yaml.dump(plan_obj, f)

    def _build_reflekt_event_file(self, events_dir: Path, event_json: dict):
        event_name = event_json.get("name")
        event_file_name = dasherize(
            underscore(
                event_json["name"]
                .replace("-", "")  # Remove *existing* hyphens in event name
                .replace("  ", " ")  # double spaces --> single spaces
                .replace(" ", "-")  # spaces --> hyphens
                .replace("/", "")  # Remove slashes
            )
        )
        event_file = events_dir / f"{event_file_name}.yml"
        logger.info(f"    Writing Reflekt event '{event_name}' to {event_file_name}.yml")
        event_obj = parse_segment_event(event_json)
        event_obj_sorted = {"version": event_obj["version"]}
        remainder_dict = funcy.omit(event_obj, "version")
        event_obj_sorted.update(remainder_dict)

        # If event file exists, then we have multiple event versions. Append this version
        if Path(event_file).is_file():
            with open(event_file, "a") as f:
                f.write("\n")
                yaml.dump(
                    [event_obj_sorted],
                    f,
                    indent=2,
                    width=70,
                    Dumper=ReflektYamlDumper,
                    sort_keys=False,
                    default_flow_style=False,
                    allow_unicode=True,
                    encoding=("utf-8"),
                )
        else:
            with open(event_file, "w") as f:
                yaml.dump(
                    [event_obj_sorted],
                    f,
                    indent=2,
                    width=70,
                    Dumper=ReflektYamlDumper,
                    sort_keys=False,
                    default_flow_style=False,
                    allow_unicode=True,
                    encoding=("utf-8"),
                )

    def _build_reflekt_identify_file(self, plan_dir: Path, traits_json: dict):
        traits = [
            parse_segment_property(name, prop_json)
            for (name, prop_json) in sorted(traits_json.items())
        ]
        traits_obj = {"traits": traits}
        traits_file = plan_dir / "user-traits.yml"

        with open(traits_file, "w") as f:
            yaml.dump(
                traits_obj,
                f,
                indent=2,
                width=70,
                Dumper=ReflektYamlDumper,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
                encoding=("utf-8"),
            )

    def _build_reflekt_group_file(self, plan_dir: Path, group_traits_json: dict):
        traits = [
            parse_segment_property(name, prop_json)
            for (name, prop_json) in sorted(group_traits_json.items())
        ]
        traits_obj = {"traits": traits}
        traits_file = plan_dir / "group-traits.yml"

        with open(traits_file, "w") as f:
            yaml.dump(
                traits_obj,
                f,
                indent=2,
                width=70,
                Dumper=ReflektYamlDumper,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
                encoding=("utf-8"),
            )
