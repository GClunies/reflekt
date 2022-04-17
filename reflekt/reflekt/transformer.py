# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import copy
import shutil
import sys

import pkg_resources
import yaml
from inflection import titleize, underscore
from loguru import logger

from reflekt.dbt.columns.reflekt import reflekt_columns
from reflekt.dbt.columns.segment import (
    seg_event_cols,
    seg_groups_cols,
    seg_identify_cols,
    seg_pages_cols,
    seg_screens_cols,
    seg_tracks_cols,
    seg_users_cols,
)
from reflekt.dbt.docs import (
    dbt_column_schema,
    dbt_model_schema,
    dbt_src_schema,
    dbt_stg_schema,
    dbt_table_schema,
)
from reflekt.logger import logger_config
from reflekt.reflekt.config import ReflektConfig
from reflekt.reflekt.dumper import ReflektYamlDumper
from reflekt.reflekt.project import ReflektProject
from reflekt.reflekt.utils import segment_2_snake
from reflekt.reflekt.warehouse import WarehouseConnection
from reflekt.segment.schema import (
    segment_event_schema,
    segment_items_schema,
    segment_payload_schema,
    segment_plan_schema,
    segment_property_schema,
)

# Setup logger
logger.configure(**logger_config)


class ReflektTransformer(object):
    """Class that accepts a reflekt tracking plan and transforms it to either:
    - CDP tracking plan
    - dbt package with sources, staging models, and docs
    """

    def __init__(self, reflekt_plan, dbt_pkg_dir=None, pkg_version=None):
        self.reflekt_plan = reflekt_plan
        self.plan_name = str.lower(self.reflekt_plan.name)
        self.reflekt_config = ReflektConfig()
        # self.cdp = self.reflekt_config.cdp
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
                "reflekt", "dbt/package/"
            )
            self.pkg_version = pkg_version
            self.db_engine = WarehouseConnection()
            self.schema_map = self.reflekt_project.schema_map
            self.schema = self._get_plan_schema_from_map(self.plan_name)
            self.src_prefix = self.reflekt_project.src_prefix
            self.stg_prefix = self.reflekt_project.stg_prefix
            self.incremental_logic = self.reflekt_project.incremental_logic

    def _get_plan_schema_from_map(self, plan_name):
        try:
            return self.schema_map[plan_name]

        except KeyError:
            logger.error(
                f"[ERROR] Tracking plan '{plan_name}' not found in "
                f"`schema_map:` in reflekt_project.yml. Please add "
                f"corresponding `{plan_name}: <schema>` key value pair to "
                f"`schema_map:`"
            )
            sys.exit(1)

    # NOTE - Avo and Iteratively only support `reflekt pull`. Avo and Iteratively
    # exist to use there UI for planning. We should not interfere!

    def _plan_rudderstack(self, reflekt_plan):
        pass

    def _plan_segment(self, reflekt_plan):
        segment_payload = copy.deepcopy(segment_payload_schema)
        segment_plan = copy.deepcopy(segment_plan_schema)
        segment_plan["display_name"] = self.plan_name
        logger.info(
            f"Converting {self.plan_name} to {titleize(self.plan_type)} " f"format"
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

    def _build_segment_trait(self, reflekt_trait):
        segment_trait = copy.deepcopy(segment_property_schema)
        segment_trait["description"] = reflekt_trait.description
        segment_trait["type"] = [reflekt_trait.type]
        segment_trait = self._handle_segment_trait(reflekt_trait, segment_trait)

        return segment_trait

    def _handle_segment_trait(self, reflekt_trait, segment_trait):
        updated_segment_trait = copy.deepcopy(segment_trait)
        if reflekt_trait.allow_null:
            updated_segment_trait["type"].append("null")
        elif reflekt_trait.type == "any":
            # If data type set to any, delete the type key in segment plan
            # (Otherwise, will trigger 'invalid argument' from Segment API)
            updated_segment_trait.pop("type", None)

        elif reflekt_trait.pattern is not None:
            updated_segment_trait["pattern"] = reflekt_trait.pattern

        elif reflekt_trait.enum is not None:
            updated_segment_trait["enum"] = reflekt_trait.enum

        if reflekt_trait.array_item_schema is not None:
            segment_array_items = self._build_segment_array_items(reflekt_trait)
            updated_segment_trait.update(segment_array_items)

        if reflekt_trait.object_properties is not None:
            segment_object_properties = self._build_segment_object_properties(
                reflekt_trait
            )
            updated_segment_trait.update(segment_object_properties)

        return updated_segment_trait

    def _build_segment_event(self, reflekt_event):
        logger.info(
            f"Building {reflekt_event.name} (version {reflekt_event.version}) "
            f"in {titleize(self.plan_type)} format"
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

    def _build_segment_property(self, reflekt_property):
        segment_property = copy.deepcopy(segment_property_schema)
        segment_property["description"] = reflekt_property.description
        segment_property["type"] = [reflekt_property.type]
        segment_property = self._handle_segment_property(
            reflekt_property, segment_property
        )

        return segment_property

    def _handle_segment_property(self, reflekt_property, segment_property):
        updated_segment_property = copy.deepcopy(segment_property)
        if hasattr(reflekt_property, "allow_null") and reflekt_property.allow_null:
            updated_segment_property["type"].append("null")

        elif hasattr(reflekt_property, "type") and reflekt_property.type == "any":
            # If data type set to any, delete the type key in segment plan
            # (Otherwise, will trigger 'invalid argument' from Segment API)
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

    def _plan_snowplow(self, reflekt_plan):
        pass

    def build_cdp_plan(self):
        # NOTE - will never push a plan to Analytics governance tool. Only `reflekt pull`
        if self.plan_type == "rudderstack":
            return self._plan_rudderstack(self.reflekt_plan)
        elif self.plan_type == "segment":
            return self._plan_segment(self.reflekt_plan)
        elif self.plan_type == "snowplow":
            return self._plan_snowplow(self.reflekt_plan)

    def _dbt_segment(self, reflekt_plan):
        logger.info(
            f"Building reflekt dbt package:\n"
            f"\n        Warehouse: {self.warehouse_type}"
            f"\n        CDP: {self.cdp_name}"
            f"\n        Tracking plan: {self.plan_name}"
            f"\n        dbt pkg path: {self.dbt_pkg_path}\n"
        )

        logger.info(f"Building dbt package at temporary path {self.tmp_pkg_dir}")
        self.db_errors = []
        dbt_src = copy.deepcopy(dbt_src_schema)
        logger.info(f"Initializing {reflekt_plan.name} dbt source")
        self._dbt_segment_source(reflekt_plan, dbt_src)
        self._dbt_segment_identifies(reflekt_plan, dbt_src)
        self._dbt_segment_users(reflekt_plan, dbt_src)
        self._dbt_segment_groups(reflekt_plan, dbt_src)
        self._dbt_segment_pages(reflekt_plan, dbt_src)
        self._dbt_segment_screens(reflekt_plan, dbt_src)
        self._dbt_segment_tracks(reflekt_plan, dbt_src)
        self._dbt_segment_event(reflekt_plan, dbt_src)
        logger.info(
            f"Writing completed {reflekt_plan.name} dbt source to dbt " f"package"
        )
        dbt_src_path = (
            self.tmp_pkg_dir
            / "models"
            / f"{self.src_prefix}{underscore(self.plan_name)}.yml"
        )

        with open(dbt_src_path, "w") as f:
            yaml.dump(
                dbt_src,
                f,
                indent=2,
                width=70,
                Dumper=ReflektYamlDumper,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
                encoding=("utf-8"),
            )

        logger.info(f"Added {reflekt_plan.name} dbt source to dbt package")
        logger.info(
            f"Copying dbt package from temporary path "
            f"{self.tmp_pkg_dir} to {self.dbt_pkg_path}"
        )

        if self.dbt_pkg_path.exists():
            shutil.rmtree(self.dbt_pkg_path)

        shutil.copytree(self.tmp_pkg_dir, self.dbt_pkg_path)
        logger.info(f"Completed building dbt package at {self.dbt_pkg_path}")

        if self.db_errors:
            logger.warning(
                f"Encountered {len(self.db_errors)} database error(s) during "
                f"dbt package build.\n\n{self.db_errors}"
            )

    def _dbt_segment_source(self, reflekt_plan, dbt_src):
        dbt_src["sources"][0]["name"] = self.schema
        dbt_src["sources"][0]["description"] = (
            f"Schema in {titleize(self.warehouse_type)} where data for the "
            f"{reflekt_plan.name} {titleize(self.cdp_name)} source is stored."
        )

    def _dbt_segment_identifies(self, reflekt_plan, dbt_src):
        if reflekt_plan.identify_traits == []:
            pass
        else:
            logger.info(
                "Templating dbt source, staging model, and docs for: identify() calls data"
            )
            idf_tbl = copy.deepcopy(dbt_table_schema)
            idf_tbl["name"] = "identifies"
            idf_tbl["description"] = (
                f"A source table with identify() calls for "
                f"{reflekt_plan.name}. Each row is a single identify "
                f"call identifying a user."
            )
            idf_sql = (  # HACK - for SQL style
                "{{\n"
                "  config(\n"
                "    materialized = 'incremental',\n"
                "    unique_key = 'identify_id',\n"
            )

            if self.warehouse_type == "redshift":
                idf_sql += "    sort = 'tstamp',\n" "    dist = 'identify_id'\n"
            elif self.warehouse_type == "snowflake":
                idf_sql += "    cluster_by = 'tstamp'\n"

            idf_sql += (  # HACK - for SQL style
                "  )\n"
                "}}\n\n"
                "with\n\n"
                "source as (\n\n"
                f"    select *\n\n"
                f"    from source {{{{ source('{underscore(self.schema)}', 'identifies') }}}}\n\n"  # noqa: E501
                f"{self.incremental_logic}\n"
                "),\n\n"
                "renamed as (\n\n"
                "    select"
            )
            idf_stg = copy.deepcopy(dbt_model_schema)
            idf_stg["name"] = (
                f"{self.stg_prefix}{underscore(self.plan_name)}" f"__identifies"
            )
            idf_stg["description"] = (
                f"A staging model with identify() calls for "
                f"{reflekt_plan.name}. Each row is a single identify "
                f"call identifying a user."
            )
            db_columns, error_msg = self.db_engine.get_columns(self.schema, "identifies")

            if error_msg is not None:
                logger.warning(f"Database error: {error_msg}. Skipping...")
                self.db_errors.append(error_msg)
            else:
                for column, mapped_columns in seg_identify_cols.items():
                    if column in db_columns or column in reflekt_columns:
                        for mapped_column in mapped_columns:
                            if mapped_column["source_name"] is not None:
                                idf_col = copy.deepcopy(dbt_column_schema)
                                idf_col["name"] = mapped_column["source_name"]
                                idf_col["description"] = mapped_column["description"]
                                idf_tbl["columns"].append(idf_col)

                            if mapped_column["schema_name"] is not None:
                                idf_col = copy.deepcopy(dbt_column_schema)
                                idf_col["name"] = mapped_column["schema_name"]
                                idf_col["description"] = mapped_column["description"]
                                idf_stg["columns"].append(idf_col)
                                sql = (
                                    mapped_column["sql"]
                                    .replace("__SCHEMA_NAME__", self.schema)
                                    .replace("__TABLE_NAME__", "identifies")
                                    .replace("__PLAN_NAME__", self.plan_name)
                                )
                                idf_sql += "\n        " + sql + ","

                for trait in reflekt_plan.identify_traits:
                    idf_col = copy.deepcopy(dbt_column_schema)
                    idf_col["name"] = segment_2_snake(trait.name)
                    idf_col["description"] = trait.description
                    idf_tbl["columns"].append(idf_col)
                    idf_stg["columns"].append(idf_col)
                    idf_sql += "\n        " + segment_2_snake(trait.name) + ","

                idf_sql = idf_sql[:-1]
                # fmt: off
                idf_sql += (  # HACK - for SQL style
                    "\n\n    from source"
                    "\n\n)"
                    "\n\n"
                    "select * from renamed\n"
                )
                # fmt: on
                dbt_src["sources"][0]["tables"].append(idf_tbl)
                dbt_stg = copy.deepcopy(dbt_stg_schema)
                dbt_stg["models"].append(idf_stg)
                idf_sql_path = (
                    self.tmp_pkg_dir
                    / "models"
                    / f"{self.stg_prefix}{underscore(self.plan_name)}__identifies.sql"  # noqa: E501
                )

                with open(idf_sql_path, "w") as f:
                    f.write(idf_sql)

                idf_stg_path = (
                    self.tmp_pkg_dir
                    / "models"
                    / "docs"
                    / f"{self.stg_prefix}{underscore(self.plan_name)}__identifies.yml"  # noqa: E501
                )

                with open(idf_stg_path, "w") as f:
                    yaml.dump(
                        dbt_stg,
                        f,
                        indent=2,
                        width=70,
                        Dumper=ReflektYamlDumper,
                        sort_keys=False,
                        default_flow_style=False,
                        allow_unicode=True,
                        encoding=("utf-8"),
                    )

    def _dbt_segment_users(self, reflekt_plan, dbt_src):
        if reflekt_plan.identify_traits == []:
            pass
        else:
            logger.info("Templating dbt source, staging model, and docs for: users data")
            users_tbl = copy.deepcopy(dbt_table_schema)
            users_tbl["name"] = "users"
            users_tbl["description"] = (
                f"A source table with the latest traits for users identified"
                f" on {reflekt_plan.name}. Each row is user."
            )
            users_sql = (  # HACK - for SQL style
                "{{\n"
                "  config(\n"
                "    materialized = 'table',\n"
                "    unique_key = 'user_id',\n"
                "  )\n"
                "}}\n\n"
                "with\n\n"
                "source as (\n\n"
                f"    select * from source {{{{ source('{underscore(self.schema)}', 'users') }}}}\n\n"  # noqa: E501
                "),\n\n"
                "renamed as (\n\n"
                "    select"
            )
            users_stg = copy.deepcopy(dbt_model_schema)
            users_stg["name"] = (
                f"{self.stg_prefix}{underscore(self.plan_name)}" f"__users"
            )
            users_stg["description"] = (
                f"A staging model with the latest traits for users "
                f"identified on {reflekt_plan.name}. Each row is user."
            )
            db_columns, error_msg = self.db_engine.get_columns(self.schema, "users")

            if error_msg is not None:
                logger.warning(f"Database error: {error_msg}. Skipping...")
                self.db_errors.append(error_msg)
            else:
                for column, mapped_columns in seg_users_cols.items():
                    if (
                        column in db_columns
                        or column in reflekt_columns
                        and column not in ["user_id", "anonymous_id"]
                    ):
                        for mapped_column in mapped_columns:
                            if mapped_column["source_name"] is not None:
                                users_col = copy.deepcopy(dbt_column_schema)
                                users_col["name"] = mapped_column["source_name"]
                                users_col["description"] = mapped_column["description"]
                                users_tbl["columns"].append(users_col)

                            if mapped_column["schema_name"] is not None:
                                users_col = copy.deepcopy(dbt_column_schema)
                                users_col["name"] = mapped_column["schema_name"]
                                users_col["description"] = mapped_column["description"]
                                users_stg["columns"].append(users_col)
                                sql = (
                                    mapped_column["sql"]
                                    .replace("__SCHEMA_NAME__", self.schema)
                                    .replace("__TABLE_NAME__", "identifies")
                                    .replace("__PLAN_NAME__", self.plan_name)
                                )
                                users_sql += "\n        " + sql + ","

                for trait in reflekt_plan.identify_traits:
                    users_col = copy.deepcopy(dbt_column_schema)
                    users_col["name"] = segment_2_snake(trait.name)
                    users_col["description"] = trait.description
                    users_tbl["columns"].append(users_col)
                    users_stg["columns"].append(users_col)
                    users_sql += "\n        " + segment_2_snake(trait.name) + ","

                users_sql = users_sql[:-1]
                # fmt: off
                users_sql += (  # HACK - for SQL style
                    "\n\n    from source"
                    "\n\n)"
                    "\n\n"
                    "select * from renamed"
                )
                # fmt: on
                dbt_src["sources"][0]["tables"].append(users_tbl)
                dbt_stg = copy.deepcopy(dbt_stg_schema)
                dbt_stg["models"].append(users_stg)
                users_sql_path = (
                    self.tmp_pkg_dir
                    / "models"
                    / f"{self.stg_prefix}{underscore(self.plan_name)}__users.sql"  # noqa: E501
                )

                with open(users_sql_path, "w") as f:
                    f.write(users_sql)

                users_stg_path = (
                    self.tmp_pkg_dir
                    / "models"
                    / "docs"
                    / f"{self.stg_prefix}{underscore(self.plan_name)}__users.yml"  # noqa: E501
                )

                with open(users_stg_path, "w") as f:
                    yaml.dump(
                        dbt_stg,
                        f,
                        indent=2,
                        width=70,
                        Dumper=ReflektYamlDumper,
                        sort_keys=False,
                        default_flow_style=False,
                        allow_unicode=True,
                        encoding=("utf-8"),
                    )

    def _dbt_segment_groups(self, reflekt_plan, dbt_src):
        if reflekt_plan.group_traits == []:
            pass
        else:
            logger.info(
                "Templating dbt source, staging model, and docs for: group() calls data"
            )
            groups_tbl = copy.deepcopy(dbt_table_schema)
            groups_tbl["name"] = "groups"
            groups_tbl["description"] = (
                f"A source table with group() calls for "
                f"{reflekt_plan.name}. Each row is a single group() "
                f"call identifying a group."
            )
            groups_sql = (  # HACK - for SQL style
                "{{\n"
                "  config(\n"
                "    materialized = 'incremental',\n"
                "    unique_key = 'group_id',\n"
            )

            if self.warehouse_type == "redshift":
                groups_sql += "    sort = 'tstamp',\n" "    dist = 'group_id'\n"
            elif self.warehouse_type == "snowflake":
                groups_sql += "    cluster_by = 'tstamp'\n"

            groups_sql += (  # HACK - for SQL style
                "  )\n"
                "}}\n\n"
                "with\n\n"
                "source as (\n\n"
                f"    select * from source {{{{ source('{underscore(self.schema)}', 'groups') }}}}\n\n"  # noqa: E501
                "),\n\n"
                "renamed as (\n\n"
                "    select"
            )
            groups_stg = copy.deepcopy(dbt_model_schema)
            groups_stg["name"] = (
                f"{self.stg_prefix}{underscore(self.plan_name)}" f"__groups"
            )
            groups_stg["description"] = (
                f"A staging model with group() calls for "
                f"{reflekt_plan.name}. Each row is a single group() "
                f"call identifying a group."
            )
            db_columns, error_msg = self.db_engine.get_columns(self.schema, "groups")

            if error_msg is not None:
                logger.warning(f"Database error: {error_msg}. Skipping...")
                self.db_errors.append(error_msg)
            else:
                for column, mapped_columns in seg_groups_cols.items():
                    if column in db_columns or column in reflekt_columns:
                        for mapped_column in mapped_columns:
                            if mapped_column["source_name"] is not None:
                                groups_col = copy.deepcopy(dbt_column_schema)
                                groups_col["name"] = mapped_column["source_name"]
                                groups_col["description"] = mapped_column["description"]
                                groups_tbl["columns"].append(groups_col)

                            if mapped_column["schema_name"] is not None:
                                groups_col = copy.deepcopy(dbt_column_schema)
                                groups_col["name"] = mapped_column["schema_name"]
                                groups_col["description"] = mapped_column["description"]
                                groups_stg["columns"].append(groups_col)
                                sql = (
                                    mapped_column["sql"]
                                    .replace("__SCHEMA_NAME__", self.schema)
                                    .replace("__TABLE_NAME__", "identifies")
                                    .replace("__PLAN_NAME__", self.plan_name)
                                )
                                groups_sql += "\n        " + sql + ","

                for trait in reflekt_plan.group_traits:
                    groups_col = copy.deepcopy(dbt_column_schema)
                    groups_col["name"] = segment_2_snake(trait.name)
                    groups_col["description"] = trait.description
                    groups_col["columns"].append(groups_col)
                    groups_stg["columns"].append(groups_col)
                    groups_sql += "\n        " + segment_2_snake(trait.name) + ","

                groups_sql = groups_sql[:-1]
                # fmt: off
                groups_sql += (  # HACK - for SQL style
                    "\n\n    from source"
                    "\n\n)"
                    "\n\n"
                    "select * from renamed\n"
                )
                # fmt: on
                dbt_src["sources"][0]["tables"].append(groups_tbl)
                dbt_stg = copy.deepcopy(dbt_stg_schema)
                dbt_stg["models"].append(groups_stg)

                groups_stg_sql_path = (
                    self.tmp_pkg_dir
                    / "models"
                    / f"{self.stg_prefix}{underscore(self.plan_name)}__groups.sql"  # noqa: E501
                )

                with open(groups_stg_sql_path, "w") as f:
                    f.write(groups_sql)

                groups_stg_path = (
                    self.tmp_pkg_dir
                    / "models"
                    / "docs"
                    / f"{self.stg_prefix}{underscore(self.plan_name)}__groups.yml"  # noqa: E501
                )

                with open(groups_stg_path, "w") as f:
                    yaml.dump(
                        dbt_stg,
                        f,
                        indent=2,
                        width=70,
                        Dumper=ReflektYamlDumper,
                        sort_keys=False,
                        default_flow_style=False,
                        allow_unicode=True,
                        encoding=("utf-8"),
                    )

    def _dbt_segment_pages(self, reflekt_plan, dbt_src):
        pages_event_list = [
            event
            for event in reflekt_plan.events
            if str.lower(event.name).replace("_", " ").replace("-", " ") == "page viewed"
        ]

        if pages_event_list == []:
            logger.info(
                f"No `Page Viewed` event found in tracking plan "
                f"{reflekt_plan.name}. Skipping."
            )
        else:
            logger.info(
                "Templating dbt source, staging model, and docs for: page() calls data"
            )
            page_viewed = pages_event_list[0]
            pages_tbl = copy.deepcopy(dbt_table_schema)
            pages_tbl["name"] = "pages"
            pages_tbl["description"] = (
                f"A source table with page() calls for "
                f"{reflekt_plan.name}. Each row is a single page view."
            )
            pages_sql = (  # HACK - for SQL style
                "{{\n"
                "  config(\n"
                "    materialized = 'incremental',\n"
                "    unique_key = 'page_id',\n"
            )

            if self.warehouse_type == "redshift":
                pages_sql += "    sort = 'tstamp',\n" "    dist = 'page_id'\n"
            elif self.warehouse_type == "snowflake":
                pages_sql += "    cluster_by = 'tstamp'\n"

            pages_sql += (  # HACK - for SQL style
                "  )\n"
                "}}\n\n"
                "with\n\n"
                "source as (\n\n"
                f"    select *\n\n"
                f"    from source {{{{ source('{underscore(self.schema)}', 'pages') }}}}\n\n"  # noqa: E501
                f"{self.incremental_logic}\n"
                "),\n\n"
                "renamed as (\n\n"
                "    select"
            )

            pages_stg = copy.deepcopy(dbt_model_schema)
            pages_stg["name"] = (
                f"{self.stg_prefix}{underscore(self.plan_name)}" f"__pages"
            )
            pages_stg["description"] = (
                f"A staging model with page() calls for "
                f"{reflekt_plan.name}. Each row is a single page "
                f"call pageing a user."
            )
            db_columns, error_msg = self.db_engine.get_columns(self.schema, "pages")

            if error_msg is not None:
                logger.warning(f"Database error: {error_msg}. Skipping...")
                self.db_errors.append(error_msg)
            else:
                for column, mapped_columns in seg_pages_cols.items():
                    if column in db_columns or column in reflekt_columns:
                        for mapped_column in mapped_columns:
                            if mapped_column["source_name"] is not None:
                                pages_col = copy.deepcopy(dbt_column_schema)
                                pages_col["name"] = mapped_column["source_name"]
                                pages_col["description"] = mapped_column["description"]
                                pages_tbl["columns"].append(pages_col)

                            if mapped_column["schema_name"] is not None:
                                pages_col = copy.deepcopy(dbt_column_schema)
                                pages_col["name"] = mapped_column["schema_name"]
                                pages_col["description"] = mapped_column["description"]
                                pages_stg["columns"].append(pages_col)
                                sql = (
                                    mapped_column["sql"]
                                    .replace("__SCHEMA_NAME__", self.schema)
                                    .replace("__TABLE_NAME__", "pages")
                                    .replace("__PLAN_NAME__", self.plan_name)
                                )
                                pages_sql += "\n        " + sql + ","

                for property in page_viewed.properties:
                    pages_col = copy.deepcopy(dbt_column_schema)
                    pages_col["name"] = segment_2_snake(property.name)
                    pages_col["description"] = property.description
                    pages_tbl["columns"].append(pages_col)
                    pages_stg["columns"].append(pages_col)
                    pages_sql += "\n        " + segment_2_snake(property.name) + ","

                pages_sql = pages_sql[:-1]
                # fmt: off
                pages_sql += (  # HACK - for SQL style
                    "\n\n    from source"
                    "\n\n)"
                    "\n\n"
                    "select * from renamed\n"
                )
                # fmt: on
                dbt_src["sources"][0]["tables"].append(pages_tbl)
                dbt_stg = copy.deepcopy(dbt_stg_schema)
                dbt_stg["models"].append(pages_stg)
                pages_sql_path = (
                    self.tmp_pkg_dir
                    / "models"
                    / f"{self.stg_prefix}{underscore(self.plan_name)}__pages.sql"  # noqa: E501
                )

                with open(pages_sql_path, "w") as f:
                    f.write(pages_sql)

                pages_stg_path = (
                    self.tmp_pkg_dir
                    / "models"
                    / "docs"
                    / f"{self.stg_prefix}{underscore(self.plan_name)}__pages.yml"  # noqa: E501
                )

                with open(pages_stg_path, "w") as f:
                    yaml.dump(
                        dbt_stg,
                        f,
                        indent=2,
                        width=70,
                        Dumper=ReflektYamlDumper,
                        sort_keys=False,
                        default_flow_style=False,
                        allow_unicode=True,
                        encoding=("utf-8"),
                    )

    def _dbt_segment_screens(self, reflekt_plan, dbt_src):
        screens_event_list = [
            event
            for event in reflekt_plan.events
            if str.lower(event.name).replace("_", " ").replace("-", " ")
            == "screen viewed"
        ]

        if screens_event_list == []:
            logger.info(
                f"No `Screen Viewed` event found in tracking plan "
                f"{reflekt_plan.name}. Skipping."
            )
        else:
            logger.info(
                "Templating dbt source, staging model, and docs for: screen() calls data"
            )
            screen_viewed = screens_event_list[0]
            screens_tbl = copy.deepcopy(dbt_table_schema)
            screens_tbl["name"] = "screens"
            screens_tbl["description"] = (
                f"A source table with screen() calls for "
                f"{reflekt_plan.name}. Each row is a single screen "
                f"view."
            )
            screens_sql = (  # HACK - for SQL style
                "{{\n"
                "  config(\n"
                "    materialized = 'incremental',\n"
                "    unique_key = 'screen_id',\n"
            )

            if self.warehouse_type == "redshift":
                screens_sql += "    sort = 'tstamp',\n" "    dist = 'screen_id'\n"
            elif self.warehouse_type == "snowflake":
                screens_sql += "    cluster_by = 'tstamp'\n"

            screens_sql += (  # HACK - for SQL style
                "  )\n"
                "}}\n\n"
                "with\n\n"
                "source as (\n\n"
                f"    select *\n\n"
                f"    from source {{{{ source('{underscore(self.schema)}', 'screens') }}}}\n\n"  # noqa: E501
                f"{self.incremental_logic}\n"
                "),\n\n"
                "renamed as (\n\n"
                "    select"
            )

            screens_stg = copy.deepcopy(dbt_model_schema)
            screens_stg["name"] = (
                f"{self.stg_prefix}{underscore(self.plan_name)}" f"__screens"
            )
            screens_stg["description"] = (
                f"A staging model with screen() calls for "
                f"{reflekt_plan.name}. Each row is a single screen "
                f"call screening a user."
            )
            db_columns, error_msg = self.db_engine.get_columns(self.schema, "screens")

            if error_msg is not None:
                logger.warning(f"Database error: {error_msg}. Skipping...")
                self.db_errors.append(error_msg)
            else:
                for column, mapped_columns in seg_screens_cols.items():
                    if column in db_columns or column in reflekt_columns:
                        for mapped_column in mapped_columns:
                            if mapped_column["source_name"] is not None:
                                screens_col = copy.deepcopy(dbt_column_schema)
                                screens_col["name"] = mapped_column["source_name"]
                                screens_col["description"] = mapped_column["description"]
                                screens_tbl["columns"].append(screens_col)

                            if mapped_column["schema_name"] is not None:
                                screens_col = copy.deepcopy(dbt_column_schema)
                                screens_col["name"] = mapped_column["schema_name"]
                                screens_col["description"] = mapped_column["description"]
                                screens_stg["columns"].append(screens_col)
                                sql = (
                                    mapped_column["sql"]
                                    .replace("__SCHEMA_NAME__", self.schema)
                                    .replace("__TABLE_NAME__", "screens")
                                    .replace("__PLAN_NAME__", self.plan_name)
                                )
                                screens_sql += "\n        " + sql + ","

                for property in screen_viewed.properties:
                    screens_col = copy.deepcopy(dbt_column_schema)
                    screens_col["name"] = segment_2_snake(property.name)
                    screens_col["description"] = property.description
                    screens_tbl["columns"].append(screens_col)
                    screens_stg["columns"].append(screens_col)
                    screens_sql += "\n        " + segment_2_snake(property.name) + ","

                screens_sql = screens_sql[:-1]
                # fmt: off
                screens_sql += (  # HACK - for SQL style
                    "\n\n    from source"
                    "\n\n)"
                    "\n\n"
                    "select * from renamed\n"
                )
                # fmt: on
                dbt_src["sources"][0]["tables"].append(screens_tbl)
                dbt_stg = copy.deepcopy(dbt_stg_schema)
                dbt_stg["models"].append(screens_stg)
                screens_sql_path = (
                    self.tmp_pkg_dir
                    / "models"
                    / f"{self.stg_prefix}{underscore(self.plan_name)}__screens.sql"  # noqa: E501
                )

                with open(screens_sql_path, "w") as f:
                    f.write(screens_sql)

                screens_stg_path = (
                    self.tmp_pkg_dir
                    / "models"
                    / "docs"
                    / f"{self.stg_prefix}{underscore(self.plan_name)}__screens.yml"  # noqa: E501
                )

                with open(screens_stg_path, "w") as f:
                    yaml.dump(
                        dbt_stg,
                        f,
                        indent=2,
                        width=70,
                        Dumper=ReflektYamlDumper,
                        sort_keys=False,
                        default_flow_style=False,
                        allow_unicode=True,
                        encoding=("utf-8"),
                    )

    def _dbt_segment_tracks(self, reflekt_plan, dbt_src):
        if len(reflekt_plan.events) == 0:
            pass
        else:
            logger.info(
                "Templating dbt source, staging model, and docs for: track() calls data"
            )
            tracks_tbl = copy.deepcopy(dbt_table_schema)
            tracks_tbl["name"] = "tracks"
            tracks_tbl["description"] = (
                f"A source table summarizing all track() calls (events) fired "
                f"on {reflekt_plan.name}. Each row is a single event. "
                f"This table summarizes all events. It does not include the "
                f"the detailed property data for each event. Each event has "
                f"its own table that contains its unique event properties "
                f"data."
            )
            tracks_sql = (  # HACK - for SQL style
                "{{\n"
                "  config(\n"
                "    materialized = 'incremental',\n"
                "    unique_key = 'event_id',\n"
            )

            if self.warehouse_type == "redshift":
                tracks_sql += "    sort = 'tstamp',\n" "    dist = 'event_id'\n"
            elif self.warehouse_type == "snowflake":
                tracks_sql += "    cluster_by = 'tstamp'\n"

            tracks_sql += (  # HACK - for SQL style
                "  )\n"
                "}}\n\n"
                "with\n\n"
                "source as (\n\n"
                f"    select *\n\n"
                f"    from source {{{{ source('{underscore(self.schema)}', 'tracks') }}}}\n\n"  # noqa: E501
                f"{self.incremental_logic}\n"
                "),\n\n"
                "renamed as (\n\n"
                "    select"
            )
            tracks_stg = copy.deepcopy(dbt_model_schema)
            tracks_stg["name"] = (
                f"{self.stg_prefix}{underscore(self.plan_name)}" f"__tracks"
            )
            tracks_stg["description"] = (
                f"A staging model summarizing all track() calls (events) fired"
                f" on {reflekt_plan.name}. Each row is a single event."
                f" This table summarizes all events. It does not include the"
                f" the detailed property data for each event. Each event has "
                f"its own table that includes the *unique event properties "
                f"data*."
            )
            db_columns, error_msg = self.db_engine.get_columns(self.schema, "tracks")

            if error_msg is not None:
                logger.warning(f"Database error: {error_msg}. Skipping...")
                self.db_errors.append(error_msg)
            else:
                for column, mapped_columns in seg_tracks_cols.items():
                    if column in db_columns or column in reflekt_columns:
                        for mapped_column in mapped_columns:
                            if mapped_column["source_name"] is not None:
                                tracks_col = copy.deepcopy(dbt_column_schema)
                                tracks_col["name"] = mapped_column["source_name"]
                                tracks_col["description"] = mapped_column["description"]
                                tracks_tbl["columns"].append(tracks_col)

                            if mapped_column["schema_name"] is not None:
                                tracks_col = copy.deepcopy(dbt_column_schema)
                                tracks_col["name"] = mapped_column["schema_name"]
                                tracks_col["description"] = mapped_column["description"]
                                tracks_stg["columns"].append(tracks_col)
                                sql = (
                                    mapped_column["sql"]
                                    .replace("__SCHEMA_NAME__", self.schema)
                                    .replace("__TABLE_NAME__", "tracks")
                                    .replace("__PLAN_NAME__", self.plan_name)
                                )
                                tracks_sql += "\n        " + sql + ","

                tracks_sql = tracks_sql[:-1]
                # fmt: off
                tracks_sql += (  # HACK - for SQL style
                    "\n\n    from source"
                    "\n\n)"
                    "\n\n"
                    "select * from renamed\n"
                )
                # fmt: on
                dbt_src["sources"][0]["tables"].append(tracks_tbl)
                dbt_stg = copy.deepcopy(dbt_stg_schema)
                dbt_stg["models"].append(tracks_stg)
                tracks_sql_path = (
                    self.tmp_pkg_dir
                    / "models"
                    / f"{self.stg_prefix}{underscore(self.plan_name)}__tracks.sql"  # noqa: E501
                )

                with open(tracks_sql_path, "w") as f:
                    f.write(tracks_sql)

                tracks_stg_path = (
                    self.tmp_pkg_dir
                    / "models"
                    / "docs"
                    / f"{self.stg_prefix}{underscore(self.plan_name)}__tracks.yml"  # noqa: E501
                )

                with open(tracks_stg_path, "w") as f:
                    yaml.dump(
                        dbt_stg,
                        f,
                        indent=2,
                        width=70,
                        Dumper=ReflektYamlDumper,
                        sort_keys=False,
                        default_flow_style=False,
                        allow_unicode=True,
                        encoding=("utf-8"),
                    )

    def _dbt_segment_event(self, reflekt_plan, dbt_src):
        if len(reflekt_plan.events) == 0:
            pass
        else:
            for event in reflekt_plan.events:
                if str.lower(event.name) in ["page viewed", "screen viewed"]:
                    pass
                else:
                    event_name = event.name
                    # Get event versions, only model the latest version
                    versions = [
                        event.version
                        for event in reflekt_plan.events
                        if event.name == event_name
                    ]

                    if event.version == max(versions):
                        logger.info(
                            f"Templating dbt source, staging model, and docs for "
                            f"event: {event.name}"
                        )
                        event_tbl = copy.deepcopy(dbt_table_schema)
                        event_tbl["name"] = segment_2_snake(event.name)
                        event_tbl["description"] = event.description
                        event_sql = (  # HACK - for SQL style
                            "{{\n"
                            "  config(\n"
                            "    materialized = 'incremental',\n"
                            "    unique_key = 'event_id',\n"
                        )

                        if self.warehouse_type == "redshift":
                            event_sql += (  # HACK - for SQL style
                                "    sort = 'tstamp',\n" "    dist = 'event_id'\n"
                            )
                        elif self.warehouse_type == "snowflake":
                            event_sql += "    cluster_by = 'tstamp'\n"

                        event_sql += (  # HACK - for SQL style
                            "  )\n"
                            "}}\n\n"
                            "with\n\n"
                            "source as (\n\n"
                            f"    select *\n\n"
                            f"    from source {{{{ source('{underscore(self.schema)}', '{segment_2_snake(event.name)}') }}}}\n\n"  # noqa: E501
                            f"{self.incremental_logic:<4}\n"
                            "),\n\n"
                            "renamed as (\n\n"
                            "    select"
                        )
                        event_stg = copy.deepcopy(dbt_model_schema)
                        event_stg["name"] = (
                            f"{self.stg_prefix}{underscore(self.plan_name)}"
                            f"__{segment_2_snake(event.name)}"
                        )
                        event_stg["description"] = event.description
                        db_columns, error_msg = self.db_engine.get_columns(
                            self.schema,
                            segment_2_snake(event.name),
                        )

                        if error_msg is not None:
                            logger.warning(f"Database error: {error_msg}. Skipping...")
                            self.db_errors.append(error_msg)
                        else:
                            for (
                                column,
                                mapped_columns,
                            ) in seg_event_cols.items():
                                if column in db_columns or column in reflekt_columns:
                                    for mapped_column in mapped_columns:
                                        if mapped_column["source_name"] is not None:
                                            event_col = copy.deepcopy(dbt_column_schema)
                                            event_col["name"] = mapped_column[
                                                "source_name"
                                            ]
                                            event_col["description"] = mapped_column[
                                                "description"
                                            ]
                                            event_tbl["columns"].append(event_col)

                                        if mapped_column["schema_name"] is not None:
                                            event_col = copy.deepcopy(dbt_column_schema)
                                            event_col["name"] = mapped_column[
                                                "schema_name"
                                            ]
                                            event_col["description"] = mapped_column[
                                                "description"
                                            ]
                                            event_stg["columns"].append(event_col)
                                            sql = (
                                                mapped_column["sql"]
                                                .replace(
                                                    "__SCHEMA_NAME__",
                                                    self.schema,
                                                )
                                                .replace(
                                                    "__TABLE_NAME__",
                                                    segment_2_snake(event.name),
                                                )
                                                .replace(
                                                    "__PLAN_NAME__",
                                                    self.plan_name,
                                                )
                                            )
                                            event_sql += "\n        " + sql + ","

                            for property in event.properties:
                                event_col = copy.deepcopy(dbt_column_schema)
                                event_col["name"] = segment_2_snake(property.name)
                                event_col["description"] = property.description
                                event_tbl["columns"].append(event_col)
                                event_stg["columns"].append(event_col)
                                event_sql += (
                                    "\n        " + segment_2_snake(property.name) + ","
                                )

                            event_sql = event_sql[:-1]
                            # fmt: off
                            event_sql += (
                                "\n\n    from source"
                                "\n\n)"
                                "\n\n"
                                "select * from renamed\n"
                            )
                            # fmt: on
                            dbt_src["sources"][0]["tables"].append(event_tbl)
                            dbt_stg = copy.deepcopy(dbt_stg_schema)
                            dbt_stg["models"].append(event_stg)
                            event_sql_path = (
                                self.tmp_pkg_dir
                                / "models"
                                / f"{self.stg_prefix}{underscore(self.plan_name)}__{segment_2_snake(event.name)}.sql"  # noqa: E501
                            )

                            with open(event_sql_path, "w") as f:
                                f.write(event_sql)

                            event_stg_path = (
                                self.tmp_pkg_dir
                                / "models"
                                / "docs"
                                / f"{self.stg_prefix}{underscore(self.plan_name)}__{segment_2_snake(event.name)}.yml"  # noqa: E501
                            )

                            with open(event_stg_path, "w") as f:
                                yaml.dump(
                                    dbt_stg,
                                    f,
                                    indent=2,
                                    width=70,
                                    Dumper=ReflektYamlDumper,
                                    sort_keys=False,
                                    default_flow_style=False,
                                    allow_unicode=True,
                                    encoding=("utf-8"),
                                )

    def build_dbt_package(self):
        """Build dbt package that models product analytics data."""
        if self.tmp_pkg_dir.exists():
            shutil.rmtree(str(self.tmp_pkg_dir))
        shutil.copytree(self.pkg_template, str(self.tmp_pkg_dir))

        # Update the version string in templated dbt_project.yml
        with open(self.tmp_pkg_dir / "dbt_project.yml", "r") as f:
            dbt_project_yml_str = f.read()

        dbt_project_yml_str = dbt_project_yml_str.replace(
            "0.1.0", str(self.pkg_version)
        ).replace("reflekt_package_name", self.dbt_package_name)

        with open(self.tmp_pkg_dir / "dbt_project.yml", "w") as f:
            f.write(dbt_project_yml_str)

        # Set dbt_pkg_name and plan_name in README.md
        with open(self.tmp_pkg_dir / "README.md", "r") as f:
            readme_str = f.read()

        readme_str = readme_str.replace("_DBT_PKG_NAME_", self.dbt_package_name).replace(
            "_PLAN_NAME_", self.plan_name
        )

        with open(self.tmp_pkg_dir / "README.md", "w") as f:
            f.write(readme_str)

        # NOTE - dbt package build logic is determined by the CDP the user sets
        # in the reflekt_config.yml file.
        if self.cdp_name == "rudderstack":
            return self._dbt_rudderstack(self.reflekt_plan)
        elif self.cdp_name == "segment":
            return self._dbt_segment(self.reflekt_plan)
        elif self.cdp_name == "snowplow":
            return self._dbt_snowplow(self.reflekt_plan)
