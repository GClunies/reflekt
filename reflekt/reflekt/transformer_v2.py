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
                segmentect_property = copy.deepcopy(segment_property_schema)
                segmentect_property["description"] = object_property["description"]
                segmentect_property["type"] = object_property["type"]
                updated_segment_property["properties"].update(
                    {object_property["name"]: segmentect_property}
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
        dbt_src = self._template_dbt_source()
        for segment_call in [
            {
                "name": "identifies",
                "description": f"A table with identify() calls fired on {reflekt_plan.name}.",
                "cdp_cols": seg_identify_cols,
            },
            {
                "name": "users",
                "description": f"A table with the latest traits for users identified on {reflekt_plan.name}.",
                "cdp_cols": seg_users_cols,
            },
            {
                "name": "groups",
                "description": f"A table with group() calls fired on {reflekt_plan.name}.",
                "cdp_cols": seg_groups_cols,
            },
            {
                "name": "pages",
                "description": f"A table with page() calls fired on {reflekt_plan.name}.",
                "cdp_cols": seg_pages_cols,
                "plan_event": [
                    event
                    for event in reflekt_plan.events
                    if str.lower(event.name).replace("_", " ").replace("-", " ")
                    == "page viewed"
                ],
            },
            {
                "name": "screens",
                "description": f"A table with screen() calls fired on {reflekt_plan.name}.",
                "cdp_cols": seg_screens_cols,
            },
            {
                "name": "tracks",
                "description": f"A table with track() event calls fired on {reflekt_plan.name}.",
                "cdp_cols": seg_tracks_cols,
            },
        ]:
            # TODO - template generic segment calls
            db_columns, error_msg = self.db_engine.get_columns(
                self.schema, segment_call["name"]
            )
            if error_msg is not None:
                logger.warning(f"Database error: {error_msg}. Skipping...")
                self.db_errors.append(error_msg)
            else:
                if segment_call["plan_event"] != []:
                    plan_event = None
                else:
                    plan_event = segment_call["plan_event"][0]

                self._template_dbt_table(
                    dbt_src=dbt_src,
                    tbl_name=segment_call["name"],
                    tbl_description=segment_call["description"],
                    db_columns=db_columns,
                    cdp_cols=segment_call["cdp_cols"],
                    plan_cols=plan_event.properties,  # TODO - how will this work for pages/screens/tracks/etc
                )

        for event in reflekt_plan.events:
            self._template_dbt_table(
                dbt_src=dbt_src,
                tbl_name=event.name,
                tbl_description=event.description,
                db_columns=db_columns,
                cdp_cols=seg_event_cols,
                plan_cols=event.properties,
            )

    def _dbt_package_snowplow(self):
        pass

    def _template_dbt_source(self, reflekt_plan: ReflektPlan):
        dbt_src = copy.deepcopy(dbt_src_schema)
        dbt_src["sources"][0]["name"] = self.schema
        dbt_src["sources"][0]["description"] = (
            f"Schema in {titleize(self.warehouse_type)} where data for the "
            f"{reflekt_plan.name} {titleize(self.cdp_name)} source is stored."
        )

        return dbt_src

    def _template_dbt_table(
        self,
        dbt_src: dict,
        tbl_name: str,
        tbl_description: str,
        db_columns: list,
        cdp_cols: dict,
        plan_cols: typing.Optional[list] = None,
    ):
        dbt_tbl = copy.deepcopy(dbt_table_schema)
        dbt_tbl["name"] = tbl_name
        dbt_tbl["description"] = tbl_description

        for column, mapped_columns in cdp_cols.items():
            if column in db_columns or column in reflekt_columns:
                for mapped_column in mapped_columns:
                    if mapped_column["source_name"] is not None:
                        tbl_col = copy.deepcopy(dbt_column_schema)
                        tbl_col["name"] = mapped_column["source_name"]
                        tbl_col["description"] = mapped_column["description"]
                        dbt_tbl["columns"].append(tbl_col)

        for column in plan_cols:
            tbl_col = copy.deepcopy(dbt_column_schema)
            tbl_col["name"] = segment_2_snake(column.name)
            tbl_col["description"] = column.description
            dbt_tbl["columns"].append(tbl_col)

        dbt_src["sources"][0]["tables"].append(dbt_tbl)

    def _template_dbt_model(self, reflekt_plan: ReflektPlan, dbt_src: dict):
        pass

    def _template_dbt_doc(self, reflekt_plan: ReflektPlan, dbt_src: dict):
        pass
