# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import shutil
from pathlib import Path

import yaml
from inflection import dasherize, underscore
from loguru import logger

from reflekt.avo.parser import parse_avo_event
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
        # If plan directory already exists, remove it.
        if plan_dir.is_dir():
            shutil.rmtree(plan_dir)
        # Re-make directories for Reflekt tracking plan(s)
        for dir in [plan_dir, events_dir]:
            if not dir.exists():
                dir.mkdir()

        self._build_reflekt_plan_file(plan_dir)

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
