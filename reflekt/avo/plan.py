# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import shutil
from pathlib import Path

import yaml
from inflection import dasherize, underscore
from loguru import logger
from reflekt.avo.parser import parse_avo_event, parse_avo_property
from reflekt.dumper import ReflektYamlDumper


class AvoPlan(object):
    def __init__(self, plan_json: dict, plan_name: str) -> None:
        self.plan_json = plan_json
        self.name = plan_name

    @classmethod
    def parse_string(cls, json_string: str) -> dict:
        parsed_json = json.loads(json_string)
        return cls(parsed_json)

    @classmethod
    def parse_file(cls, json_file_path: Path) -> dict:
        with open(json_file_path, "r") as f:
            contents = f.read()
        return cls.parse_string(contents)

    def build_reflekt(self, plan_dir: Path) -> None:
        events_dir = plan_dir / "events"

        if plan_dir.is_dir():  # Always start from a clean Reflekt plan
            shutil.rmtree(plan_dir)

        for dir in [plan_dir, events_dir]:  # Remake Reflekt plan directories
            if not dir.exists():
                dir.mkdir()

        self._build_reflekt_plan_file(plan_dir)
        user_traits_json = None  # TODO - remove when Reflekt pulls from Avo Export API
        # user_traits_json = (
        #     self.plan_json.get("rules")  # Segment logic, update once using Export API
        #     .get("identify", {})
        #     .get("properties", {})
        #     .get("traits", {})
        #     .get("properties")
        # )
        logger.info("    Writing Reflekt user traits to user-traits.yml")
        self._build_reflekt_user_traits(plan_dir, user_traits_json)
        group_traits_json = None  # TODO - remove when Reflekt pulls from Avo Export API
        # group_traits_json = (
        #     self.plan_json.get("rules")  # Segment logic, update once using Export API
        #     .get("group", {})
        #     .get("properties", {})
        #     .get("traits", {})
        #     .get("properties")
        # )
        logger.info("    Writing Reflekt group traits to group-traits.yml")
        self._build_reflekt_group_traits(plan_dir, group_traits_json)

        for event_json in self.plan_json.get("events", []):
            self._build_reflekt_event_file(events_dir, event_json)

    def _build_reflekt_plan_file(self, plan_dir: Path) -> None:
        plan_file = plan_dir / "plan.yml"
        plan_obj = {"name": self.name}
        with open(plan_file, "w") as f:
            yaml.dump(plan_obj, f)

    def _build_reflekt_event_file(self, events_dir: Path, event_json: dict) -> None:
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
        logger.info(f"    Building Reflekt event '{event_name}'")
        event_obj = parse_avo_event(event_json)
        event_obj_with_version = {"version": 1}  # No event versions in Avo. Set to 1
        event_obj_with_version.update(event_obj)

        with open(event_file, "w") as f:
            yaml.dump(
                [event_obj_with_version],
                f,
                indent=2,
                width=70,
                Dumper=ReflektYamlDumper,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
                encoding=("utf-8"),
            )

    # TODO - update when Reflekt pulls from Avo Export API
    def _build_reflekt_user_traits(self, plan_dir: Path, user_traits_json: dict):
        if user_traits_json is None:
            traits = []
        else:
            traits = [
                parse_avo_property(name, prop_json)
                for (name, prop_json) in sorted(user_traits_json.items())
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

    # TODO - update this when Reflekt pulls from Avo Export API
    def _build_reflekt_group_traits(self, plan_dir: Path, group_traits_json: dict):
        if group_traits_json is None:
            traits = []
        else:
            traits = [
                parse_avo_property(name, prop_json)
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
