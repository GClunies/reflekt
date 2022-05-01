# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import copy
import shutil
import typing
from pathlib import Path

import pkg_resources
import yaml
from inflection import titleize, underscore
from loguru import logger
from packaging.version import Version

from reflekt.logger import logger_config
from reflekt.reflekt.columns import reflekt_columns
from reflekt.reflekt.config import ReflektConfig
from reflekt.reflekt.dbt_templater import (
    dbt_column_schema,
    dbt_model_schema,
    dbt_src_schema,
    dbt_stg_schema,
    dbt_table_schema,
)
from reflekt.reflekt.dumper import ReflektYamlDumper
from reflekt.reflekt.event import ReflektEvent
from reflekt.reflekt.plan import ReflektPlan
from reflekt.reflekt.project import ReflektProject
from reflekt.reflekt.property import ReflektProperty
from reflekt.reflekt.trait import ReflektTrait
from reflekt.reflekt.utils import segment_2_snake
from reflekt.reflekt.warehouse import WarehouseConnection
from reflekt.segment.columns import (
    seg_event_cols,
    seg_groups_cols,
    seg_identify_cols,
    seg_pages_cols,
    seg_screens_cols,
    seg_tracks_cols,
    seg_users_cols,
)
from reflekt.segment.schema import (
    segment_event_schema,
    segment_items_schema,
    segment_payload_schema,
    segment_plan_schema,
    segment_property_schema,
)


class ReflektTransformer(object):
    def __init__(
        self,
        reflekt_plan: ReflektPlan,
        dbt_pkg_dir: typing.Optional[Path] = None,
        pkg_version: typing.Optional[Version] = None,
    ):
        logger.configure(**logger_config)
        self.reflekt_plan = reflekt_plan
        self.plan_name = str.lower(self.reflekt_plan.name)
        self.dbt_package_schema = self.reflekt_plan.dbt_package_schema
        self.reflekt_config = ReflektConfig()
        self.cdp_name = self.reflekt_config.cdp_name
        self.plan_type = self.reflekt_config.plan_type
        self.warehouse = self.reflekt_config.warehouse
        self.warehouse_type = self.reflekt_config.warehouse_type
        if dbt_pkg_dir is not None:
            self.reflekt_project = ReflektProject()
            self.project_dir = self.reflekt_project.project_dir
            self.dbt_package_name = f"reflekt_{underscore(self.reflekt_plan.name)}"
            self.tmp_pkg_dir = (
                self.project_dir / ".reflekt" / "tmp" / self.dbt_package_name
            )
            self.dbt_pkg_path = dbt_pkg_dir / self.dbt_package_name
            self.pkg_template = pkg_resources.resource_filename(
                "reflekt", "templates/dbt/"
            )
            self.pkg_version = pkg_version
            self.db_engine = WarehouseConnection()
            self.plan_db_schemas = self.reflekt_project.plan_db_schemas
            self.schema = self._get_plan_db_schema(self.plan_name)
            self.src_prefix = self.reflekt_project.src_prefix
            self.model_prefix = self.reflekt_project.model_prefix
            self.incremental_logic = self.reflekt_project.incremental_logic

    def _get_plan_db_schema(self, plan_name: str):
        try:
            return self.plan_db_schemas[plan_name]

        except KeyError:
            raise KeyError(
                f"Tracking plan '{plan_name}' not found in "
                f"`plan_db_schemas:` in reflekt_project.yml. Please add "
                f"corresponding `{plan_name}: <schema>` key value pair."
            )

    def build_cpd_plan(self):
        pass

    # NOTE - Avo and Iteratively only support `reflekt pull`.

    def _plan_rudderstack(self):
        pass

    def _plan_segment(self, reflekt_plan: ReflektPlan):
        segment_payload = copy.deepcopy(segment_payload_schema)
        segment_plan = copy.deepcopy(segment_plan_schema)
        segment_plan["display_name"] = self.plan_name
        logger.info(
            f"Converting reflekt plan {self.plan_name} to {titleize(self.plan_type)} "
            f"format"
        )

        if reflekt_plan.events != []:
            for reflekt_event in reflekt_plan.events:
                segment_event = self._build_segment_event(reflekt_event)
                segment_plan["rules"]["events"].append(segment_event)

        if reflekt_plan.identify_traits != []:
            for reflekt_identify_trait in reflekt_plan.identify_traits:
                segment_identify_trait = self._build_segment_trait(
                    reflekt_identify_trait
                )

                if reflekt_identify_trait.required:
                    segment_plan["rules"]["identify"]["properties"]["traits"][
                        "required"
                    ].append(reflekt_identify_trait.name)

                segment_plan["rules"]["identify"]["properties"]["traits"][
                    "properties"
                ].update({reflekt_identify_trait.name: segment_identify_trait})

        if reflekt_plan.group_traits != []:
            for reflekt_group_trait in reflekt_plan.group_traits:
                segment_group_trait = self._build_segment_trait(reflekt_group_trait)

                if reflekt_group_trait.required:
                    segment_plan["rules"]["group"]["properties"]["traits"][
                        "required"
                    ].append(reflekt_group_trait.name)

                segment_plan["rules"]["group"]["properties"]["traits"][
                    "properties"
                ].update({reflekt_group_trait.name: segment_group_trait})

        segment_payload["tracking_plan"].update(segment_plan)

        return segment_payload

    def _build_segment_event(self, reflekt_event: ReflektEvent):
        if reflekt_event.version > 1:
            version_str = f"(version {reflekt_event.version}) "
        else:
            version_str = ""

        logger.info(
            f"Building {reflekt_event.name} {version_str} in "
            f"{titleize(self.plan_type)} format"
        )
        segment_event = copy.deepcopy(segment_event_schema)
        segment_event["name"] = reflekt_event.name
        segment_event["description"] = reflekt_event.description
        segment_event["version"] = reflekt_event.version
        segment_event["rules"]["labels"] = reflekt_event.metadata

        for reflekt_property in reflekt_event.properties:
            segment_property = self._build_segment_property(reflekt_property)

            if reflekt_property.required:
                segment_event["rules"]["properties"]["properties"]["required"].append(
                    reflekt_property.name
                )

            segment_event["rules"]["properties"]["properties"]["properties"].update(
                {reflekt_property.name: segment_property}
            )

        return segment_event

    def _build_segment_property(self, reflekt_property: ReflektProperty):
        segment_property = copy.deepcopy(segment_property_schema)
        segment_property["description"] = reflekt_property.description
        segment_property["type"] = [reflekt_property.type]
        segment_property = self._parse_reflekt_property(
            reflekt_property, segment_property
        )

        return segment_property

    def _parse_reflekt_property(
        self, reflekt_property: ReflektProperty, segment_property: dict
    ):
        updated_segment_property = copy.deepcopy(segment_property)
        if hasattr(reflekt_property, "allow_null") and reflekt_property.allow_null:
            updated_segment_property["type"].append("null")
        elif hasattr(reflekt_property, "type") and reflekt_property.type == "any":
            # If data type is 'any', delete type key. Otherwise, triggers 'invalid argument' from Segment API)  # noqa: E501
            updated_segment_property.pop("type", None)
        elif (
            hasattr(reflekt_property, "pattern") and reflekt_property.pattern is not None
        ):
            updated_segment_property["pattern"] = reflekt_property.pattern
        elif hasattr(reflekt_property, "enum") and reflekt_property.enum is not None:
            updated_segment_property["enum"] = reflekt_property.enum
        elif hasattr(reflekt_property, "datetime") and reflekt_property.datetime:
            updated_segment_property["format"] = "date-time"

        if (
            hasattr(reflekt_property, "array_item_schema")
            and reflekt_property.array_item_schema is not None
        ):
            segment_array_items = copy.deepcopy(segment_items_schema)
            for reflekt_item_property in reflekt_property.array_item_schema:
                segment_item_property = copy.deepcopy(segment_property_schema)
                segment_item_property["description"] = reflekt_item_property[
                    "description"
                ]
                segment_item_property["type"] = [reflekt_item_property["type"]]
                segment_item_property = self._handle_segment_property(
                    reflekt_item_property, segment_item_property
                )

                if (
                    "required" in reflekt_item_property
                    and reflekt_item_property["required"]
                ):
                    segment_array_items["items"]["required"].append(
                        reflekt_item_property["name"]
                    )

                segment_array_items["items"]["properties"].update(
                    {reflekt_item_property["name"]: segment_item_property}
                )

            updated_segment_property.update(segment_array_items)

        if (
            hasattr(reflekt_property, "object_properties")
            and reflekt_property.object_properties is not None
        ):
            updated_segment_property["properties"] = {}
            updated_segment_property["required"] = []

            for object_property in reflekt_property.object_properties:
                segment_object_property = copy.deepcopy(segment_property_schema)
                segment_object_property["description"] = object_property["description"]
                segment_object_property["type"] = object_property["type"]
                updated_segment_property["properties"].update(
                    {object_property["name"]: segment_object_property}
                )

                if "required" in object_property and object_property["required"]:
                    updated_segment_property["required"].append(object_property["name"])

        return updated_segment_property

    def _build_segment_trait(self, reflekt_trait: ReflektTrait):
        segment_trait = copy.deepcopy(segment_property_schema)
        segment_trait["description"] = reflekt_trait.description
        segment_trait["type"] = [reflekt_trait.type]
        segment_trait = self._parse_reflekt_trait(reflekt_trait, segment_trait)

        return segment_trait

    def _parse_reflekt_trait(self, reflekt_trait: ReflektTrait, segment_trait: dict):
        updated_segment_trait = copy.deepcopy(segment_trait)
        if reflekt_trait.allow_null:
            updated_segment_trait["type"].append("null")
        elif reflekt_trait.type == "any":
            # If data type is 'any', delete type key. Otherwise, triggers 'invalid argument' from Segment API)  # noqa: E501
            updated_segment_trait.pop("type", None)
        elif reflekt_trait.pattern is not None:
            updated_segment_trait["pattern"] = reflekt_trait.pattern
        elif reflekt_trait.enum is not None:
            updated_segment_trait["enum"] = reflekt_trait.enum

        # NOTE - reflekt does not support traits with type = array|object

        return updated_segment_trait

    def _plan_snowplow(self):
        pass

    def build_dbt_package(self, reflekt_plan: ReflektPlan):
        pass

    def _dbt_package_rudderstack(self):
        pass

    def _dbt_package_segment(self, reflekt_plan: ReflektPlan):
        logger.info(
            f"Building reflekt dbt package:\n"
            f"\n        Warehouse: {self.warehouse_type}"
            f"\n        CDP: {self.cdp_name}"
            f"\n        Tracking plan: {self.plan_name}"
            f"\n        dbt pkg path: {self.dbt_pkg_path}\n"
        )
        self.db_errors = []
        dbt_src_obj = self._template_dbt_source()
        for segment_call in ["identifies", "users", "pages", "screens", "tracks"]:
            # TODO - template generic segment calls
            pass

        for event in reflekt_plan.events:
            # TODO - template unique event calls from reflekt trackign plan
            pass

    def _dbt_package_snowplow(self):
        pass

    def _template_dbt_source(self, reflekt_plan: ReflektPlan):
        dbt_src_obj = copy.deepcopy(dbt_src_schema)
        dbt_src_obj["sources"][0]["name"] = self.schema
        dbt_src_obj["sources"][0]["description"] = (
            f"Schema in {titleize(self.warehouse_type)} where data for the "
            f"{reflekt_plan.name} {titleize(self.cdp_name)} source is stored."
        )

        return dbt_src_obj

    def _template_dbt_table(self, reflekt_plan: ReflektPlan, dbt_src_obj: dict):
        pass

    def _template_dbt_model(self, reflekt_plan: ReflektPlan, dbt_src_obj: dict):
        pass

    def _template_dbt_doc(self, reflekt_plan: ReflektPlan, dbt_src_obj: dict):
        pass
