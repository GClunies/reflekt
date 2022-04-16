# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
# SPDX-License-Identifier: Apache-2.0
#
# SPDX-FileCopyrightText: 2021 Buffer
# SPDX-License-Identifier: MIT

import json
import os
import shutil

from loguru import logger
from reflekt.logger import logger_config

import yaml
import funcy
from pathlib import Path
from inflection import dasherize, underscore
from reflekt.segment.parser import (
    parse_segment_event,
    parse_segment_property,
)
from reflekt.reflekt.dumper import ReflektYamlDumper

logger.configure(**logger_config)


# The class SegmentPlan is a derivative work based on the class
# JsonTrackingPlan from project tracking-plan-kit licensed under MIT. All
# changes are licensed under Apache-2.0.
class SegmentPlan(object):
    def __init__(self, plan_json):
        self.plan_json = plan_json

    @classmethod
    def parse_string(cls, json_string):
        parsed_json = json.loads(json_string)
        plan = cls(parsed_json)

        return plan

    @classmethod
    def parse_file(cls, json_file_path):
        with open(json_file_path, "r") as f:
            contents = f.read()
            return cls.parse_string(contents)

    @property
    def display_name(self):
        return self.plan_json.get("display_name")

    @property
    def name(self):
        return self.plan_json.get("name")

    def build_reflekt(self, plan_dir):
        events_dir = os.path.join(plan_dir, "events")
        # If the plan directory already exists, remove it.
        # Ensures we are starting from a "clean slate"
        if os.path.isdir(plan_dir):
            shutil.rmtree(plan_dir)
        # Re-make directories for reflekt tracking plan(s)
        for dir in [plan_dir, events_dir]:
            if not os.path.exists(dir):
                os.makedirs(dir)

        logger.info(f"Building reflekt plan at {plan_dir}")

        # Build reflekt plan
        self._build_reflekt_plan_file(plan_dir)

        traits_json = (
            self.plan_json.get("rules")
            .get("identify", {})
            .get("properties", {})
            .get("traits", {})
            .get("properties")
        )

        # Build reflekt identify traits
        if traits_json:
            logger.info(f"Building reflekt identify traits at {plan_dir}/identify.yml")
            self._build_reflekt_identify_file(plan_dir, traits_json)

        group_traits_json = (
            self.plan_json.get("rules")
            .get("group", {})
            .get("properties", {})
            .get("traits", {})
            .get("properties")
        )

        # Build reflekt group traits
        if group_traits_json:
            logger.info(f"Building reflekt group traits at {plan_dir}/group.yml")
            self._build_reflekt_group_file(plan_dir, group_traits_json)

        # Build reflekt events
        for event_json in self.plan_json.get("rules", {}).get("events", []):
            self._build_reflekt_event_file(events_dir, event_json)

    def _build_reflekt_plan_file(self, plan_dir):
        plan_file = os.path.join(plan_dir, "plan.yml")

        plan_obj = {
            "name": self.display_name
        }  # Segment refers to the plan name as the `display_name` in their API

        with open(plan_file, "w") as f:
            yaml.dump(plan_obj, f)

    def _build_reflekt_event_file(self, events_dir, event_json):
        event_name = event_json.get("name")
        event_file_name = dasherize(
            underscore(event_json["name"].replace(" ", "-").replace("/", ""))
        )
        event_file = os.path.join(events_dir, f"{event_file_name}.yml")

        logger.info(f"Building reflekt event `{event_name}` at {event_file}")
        event_obj = parse_segment_event(event_json)

        event_obj_sorted = {"version": event_obj["version"]}
        remainder_dict = funcy.omit(event_obj, "version")
        event_obj_sorted.update(remainder_dict)

        if Path(event_file).is_file():
            # Event file already exists due to multiple versions. Append this
            # version to the event file.
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

    def _build_reflekt_identify_file(self, plan_dir, traits_json):
        traits = [
            parse_segment_property(name, prop_json)
            for (name, prop_json) in traits_json.items()
        ]

        traits_obj = {"traits": traits}
        traits_file = os.path.join(plan_dir, "identify_traits.yml")

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

    def _build_reflekt_group_file(self, plan_dir, group_traits_json):
        traits = [
            parse_segment_property(name, prop_json)
            for (name, prop_json) in group_traits_json.items()
        ]

        traits_obj = {"traits": traits}
        traits_file = os.path.join(plan_dir, "group_traits.yml")

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
