# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import copy
import shutil
from pathlib import Path
from typing import Optional, Union

import pkg_resources
import yaml
from inflection import titleize, underscore
from loguru import logger
from packaging.version import Version

from reflekt.config import ReflektConfig
from reflekt.constants import REFLEKT_RESERVED_COLUMNS, REFLEKT_TEMPLATE_COLUMNS
from reflekt.dbt import (
    dbt_column_schema,
    dbt_doc_schema,
    dbt_model_schema,
    dbt_src_schema,
    dbt_table_schema,
)
from reflekt.dumper import ReflektYamlDumper
from reflekt.event import ReflektEvent
from reflekt.plan import ReflektPlan
from reflekt.project import ReflektProject
from reflekt.property import ReflektProperty
from reflekt.segment.columns import (
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
from reflekt.trait import ReflektTrait
from reflekt.utils import segment_2_snake
from reflekt.warehouse import WarehouseConnection


class ReflektTransformer(object):
    def __init__(
        self,
        reflekt_plan: ReflektPlan,
        models_subfolder: Optional[str] = None,
        dbt_package_version: Optional[Version] = None,
    ) -> None:
        self.reflekt_plan = reflekt_plan
        self.plan_name = str.lower(self.reflekt_plan.name)
        self.reflekt_config = ReflektConfig()
        self.cdp_name = self.reflekt_config.cdp_name
        self.plan_type = self.reflekt_config.plan_type
        self.warehouse = self.reflekt_config.warehouse
        self.warehouse_type = self.reflekt_config.warehouse_type
        if reflekt_plan.database is not None:
            self.database = reflekt_plan.database
            self.schema = reflekt_plan.schema
            self.schema_alias = reflekt_plan.schema_alias
            self.reflekt_project = ReflektProject()
            self.project_dir = self.reflekt_project.project_dir
            self.dbt_package_name = (
                f"reflekt_{self.reflekt_project.name}_{self.cdp_name}"
            )
            self.dbt_package_version = dbt_package_version
            self.dbt_pkg_dir = self.project_dir / "dbt-packages" / self.dbt_package_name
            self.tmp_pkg_dir = (
                self.project_dir / ".reflekt" / "tmp" / self.dbt_package_name
            )
            self.models_subfolder = models_subfolder
            self.blank_dbt_pkg = pkg_resources.resource_filename(
                "reflekt", "templates/dbt/"
            )
            self.db_engine = WarehouseConnection()
            self.src_prefix = self.reflekt_project.src_prefix
            self.model_prefix = self.reflekt_project.model_prefix
            self.materialized = self.reflekt_project.materialized
            self.incremental_logic = self.reflekt_project.incremental_logic
            self.docs_prefix = self.reflekt_project.docs_prefix
            self.docs_test_not_null = self.reflekt_project.docs_test_not_null
            self.docs_test_unique = self.reflekt_project.docs_test_unique
            self.docs_in_folder = self.reflekt_project.docs_in_folder

    def build_cdp_plan(self, plan_type: Optional[str] = None) -> None:
        if plan_type is None:
            plan_type = self.plan_type

        if plan_type.lower() == "rudderstack":
            return self._build_plan_rudderstack(self.reflekt_plan)
        elif plan_type.lower() == "segment":
            return self._build_plan_segment(self.reflekt_plan)
        elif plan_type.lower() == "snowplow":
            return self._build_plan_snowplow(self.reflekt_plan)
        # 'reflekt push' not supported for Avo or Iteratively.

    def _build_plan_rudderstack(self):
        pass

    def _build_plan_snowplow(self):
        pass

    def _build_plan_segment(self, reflekt_plan: ReflektPlan) -> dict:
        segment_payload = copy.deepcopy(segment_payload_schema)
        segment_plan = copy.deepcopy(segment_plan_schema)
        segment_plan["display_name"] = self.plan_name
        logger.info("")  # Terminal newline
        logger.info(
            f"Converting Reflekt tracking plan '{self.plan_name}' to "
            f"{titleize(self.plan_type)} format"
        )

        if reflekt_plan.events != []:
            for reflekt_event in reflekt_plan.events:
                segment_event = self._build_segment_event(reflekt_event)
                segment_plan["rules"]["events"].append(segment_event)

        if reflekt_plan.user_traits != []:
            for reflekt_identify_trait in reflekt_plan.user_traits:
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

    def _build_segment_event(self, reflekt_event: ReflektEvent) -> dict:
        if reflekt_event.version > 1:
            version_str = f" (version {reflekt_event.version})"
        else:
            version_str = ""

        logger.info(f"    Converting '{reflekt_event.name}'{version_str}")
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

    def _build_segment_property(self, reflekt_property: ReflektProperty) -> dict:
        segment_property = copy.deepcopy(segment_property_schema)
        segment_property["description"] = reflekt_property.description
        segment_property["type"] = [reflekt_property.type]
        segment_property = self._parse_reflekt_property(
            reflekt_property, segment_property
        )

        return segment_property

    def _parse_reflekt_property(
        self,
        reflekt_property: Union[ReflektProperty, ReflektTrait],
        segment_property: dict,
    ) -> dict:
        # ReflektTrait is a child class of ReflektProperty, so this
        # instance method will parse Reflekt properties and traits
        updated_segment_property = copy.deepcopy(segment_property)
        if hasattr(reflekt_property, "allow_null") and reflekt_property.allow_null:
            updated_segment_property["type"].append("null")
        elif hasattr(reflekt_property, "type") and reflekt_property.type == "any":
            # If data type is 'any', delete type key. Otherwise, triggers
            # 'invalid argument' from Segment API
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
                segment_item_property = self._parse_reflekt_property(
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
                segment_property = copy.deepcopy(segment_property_schema)
                segment_property["description"] = object_property["description"]
                segment_property["type"] = object_property["type"]
                updated_segment_property["properties"].update(
                    {object_property["name"]: segment_property}
                )

                if "required" in object_property and object_property["required"]:
                    updated_segment_property["required"].append(object_property["name"])

        return updated_segment_property

    def _build_segment_trait(self, reflekt_trait: ReflektTrait) -> dict:
        segment_trait = copy.deepcopy(segment_property_schema)
        segment_trait["description"] = reflekt_trait.description
        segment_trait["type"] = [reflekt_trait.type]
        # _parse_reflekt_property works on traits too
        segment_trait = self._parse_reflekt_property(reflekt_trait, segment_trait)

        return segment_trait

    def check_for_schema_match(self) -> None:
        pass

    def build_dbt_package(self) -> None:
        self.db_errors = []
        logger.info(
            f"Building Reflekt dbt package:"
            f"\n        dbt package name: {self.dbt_package_name}"
            f"\n        dbt package version: {self.dbt_package_version}"
            f"\n        dbt package directory: {self.dbt_pkg_dir}"
            f"\n        cdp: {self.cdp_name}"
            f"\n        analytics governance tool: {self.plan_type}"
            f"\n        tracking plan: {self.plan_name}"
            f"\n        warehouse: {self.warehouse_type}"
            f"\n        schema: {self.schema}"
            f"\n        schema_alias: {self.reflekt_plan.schema_alias}"
            f"\n        models subdirectory: models/{self.models_subfolder}\n"
        )

        if self.dbt_pkg_dir.exists():  # If dbt pkg exists, use as base for temp pkg
            if self.tmp_pkg_dir.exists():  # Clean any existing temp pkg
                shutil.rmtree(self.tmp_pkg_dir)
            shutil.copytree(self.dbt_pkg_dir, str(self.tmp_pkg_dir))
        else:  # dbt pkg does not exist, start with blank dbt pkg
            if self.tmp_pkg_dir.exists():  # Ensure tmp dir is empty
                shutil.rmtree(self.tmp_pkg_dir)
            shutil.copytree(self.blank_dbt_pkg, str(self.tmp_pkg_dir))

        # Update version in templated dbt_project.yml
        with open(self.tmp_pkg_dir / "dbt_project.yml", "r") as f:
            dbt_project_yml_str = f.read()

        dbt_project_yml_str = dbt_project_yml_str.replace(
            "0.1.0", str(self.dbt_package_version)  # Template always has version '0.1.0'
        ).replace("reflekt_package_name", self.dbt_package_name)

        with open(self.tmp_pkg_dir / "dbt_project.yml", "w") as f:
            f.write(dbt_project_yml_str)

        # Set dbt_pkg_name and plan_name in README.md
        with open(self.tmp_pkg_dir / "README.md", "r") as f:
            readme_str = f.read()

        readme_str = readme_str.replace("_DBT_PKG_NAME_", self.dbt_package_name).replace(
            "_PLAN_TOOL_", titleize(self.reflekt_plan.plan_type)
        )

        with open(self.tmp_pkg_dir / "README.md", "w") as f:
            f.write(readme_str)

        # Create models subfolder if it doesn't already exists
        models_subfolder_dir = self.tmp_pkg_dir / "models" / self.models_subfolder

        if not models_subfolder_dir.exists():
            models_subfolder_dir.mkdir(parents=True, exist_ok=True)

        if self.cdp_name == "rudderstack":
            return self._dbt_package_rudderstack(self.reflekt_plan)
        elif self.cdp_name == "segment":
            return self._dbt_package_segment(self.reflekt_plan)
        elif self.cdp_name == "snowplow":
            return self._dbt_package_snowplow(self.reflekt_plan)

    def _dbt_package_rudderstack(
        self,
        reflekt_plan: ReflektPlan,
    ) -> None:
        pass

    def _dbt_package_snowplow(
        self,
        reflekt_plan: ReflektPlan,
    ) -> None:
        pass

    def _dbt_package_segment(
        self,
        reflekt_plan: ReflektPlan,
    ) -> None:
        dbt_src = self._template_dbt_source(reflekt_plan=reflekt_plan)

        std_segment_tables = []
        if self.reflekt_plan.user_traits:
            std_segment_tables.append(
                {
                    "name": "identifies",
                    "description": "A table with identify() calls.",
                    "unique_key": "identify_id",
                    "cdp_cols": seg_identify_cols,
                    "plan_cols": reflekt_plan.user_traits,
                }
            )
            std_segment_tables.append(
                {
                    "name": "users",
                    "description": "A table with the latest traits for users.",
                    "unique_key": "user_id",
                    "cdp_cols": seg_users_cols,
                    "plan_cols": reflekt_plan.user_traits,
                }
            )

        if self.reflekt_plan.group_traits:
            std_segment_tables.append(
                {
                    "name": "groups",
                    "description": "A table with group() calls.",
                    "unique_key": "group_id",
                    "cdp_cols": seg_groups_cols,
                    "plan_cols": reflekt_plan.group_traits,
                }
            )

        if self.reflekt_plan.events:
            std_segment_tables.append(
                {
                    "name": "tracks",
                    "description": "A table with event track() calls.",
                    "unique_key": "event_id",
                    "cdp_cols": seg_tracks_cols,
                    "plan_cols": [],
                }
            )

        for std_segment_table in std_segment_tables:
            db_columns, error_msg = self.db_engine.get_columns(
                self.schema, std_segment_table["name"]
            )
            if error_msg is not None:
                self.db_errors.append(error_msg)
            else:
                table_name = std_segment_table["name"]
                model_name = (
                    f"{self.model_prefix}{self.schema}__{table_name}"
                    if self.schema_alias is None
                    else f"{self.model_prefix}{self.schema_alias}__{table_name}"
                )
                doc_name = (
                    f"{self.docs_prefix}{self.schema}__{table_name}"
                    if self.schema_alias is None
                    else f"{self.docs_prefix}{self.schema_alias}__{table_name}"
                )
                self._template_dbt_table(
                    dbt_src=dbt_src,
                    table_name=table_name,
                    table_description=std_segment_table["description"],
                )
                self._template_dbt_model(
                    models_subfolder=self.models_subfolder,
                    materialized=self.materialized,
                    unique_key=std_segment_table["unique_key"],
                    table_name=table_name,
                    model_name=model_name,
                    db_columns=db_columns,
                    cdp_cols=std_segment_table["cdp_cols"],
                    plan_cols=std_segment_table["plan_cols"],
                )
                self._template_dbt_doc(
                    models_subfolder=self.models_subfolder,
                    doc_name=doc_name,
                    model_name=model_name,
                    model_description=std_segment_table["description"],
                    db_columns=db_columns,
                    cdp_cols=std_segment_table["cdp_cols"],
                    plan_cols=std_segment_table["plan_cols"],
                )

        for event in self.reflekt_plan.events:
            event_name_lower = str.lower(event.name).replace("_", " ").replace("-", " ")
            if event_name_lower == "page viewed":
                table_name = "pages"
                unique_key = "page_id"
                cdp_cols = seg_pages_cols
            elif event_name_lower == "screen viewed":
                table_name = "screens"
                unique_key = "screen_id"
                cdp_cols = seg_screens_cols
            else:
                table_name = segment_2_snake(event.name)
                unique_key = "event_id"
                cdp_cols = seg_tracks_cols

            # Get event versions
            multi_version_event_list = [
                x for x in reflekt_plan.events if x.name == event.name
            ]
            event_versions = [event.version for event in multi_version_event_list]

            # Only template latest version of event
            if event.version == max(event_versions):
                db_columns, error_msg = self.db_engine.get_columns(
                    self.schema, table_name
                )
                if error_msg is not None:
                    self.db_errors.append(error_msg)
                else:
                    model_name = (
                        f"{self.model_prefix}{self.schema}__{table_name}"
                        if self.schema_alias is None
                        else f"{self.model_prefix}{self.schema_alias}__{table_name}"
                    )
                    doc_name = (
                        f"{self.docs_prefix}{self.schema}__{table_name}"
                        if self.schema_alias is None
                        else f"{self.docs_prefix}{self.schema_alias}__{table_name}"
                    )
                    self._template_dbt_table(
                        dbt_src=dbt_src,
                        table_name=table_name,
                        table_description=event.description,
                    )
                    self._template_dbt_model(
                        models_subfolder=self.models_subfolder,
                        materialized=self.materialized,
                        unique_key=unique_key,
                        table_name=table_name,
                        model_name=model_name,
                        db_columns=db_columns,
                        cdp_cols=cdp_cols,
                        plan_cols=event.properties,
                        event_name=event.name,
                    )
                    self._template_dbt_doc(
                        models_subfolder=self.models_subfolder,
                        doc_name=doc_name,
                        model_name=model_name,
                        model_description=event.description,
                        db_columns=db_columns,
                        cdp_cols=cdp_cols,
                        plan_cols=event.properties,
                    )

        src_name = (
            f"{self.src_prefix}{self.schema}"
            if self.schema_alias is None
            else f"{self.src_prefix}{self.schema_alias}"
        )

        if self.docs_in_folder:
            docs_folder_str = (
                str(self.tmp_pkg_dir) + f"/models/{self.models_subfolder}/docs"
            )
            docs_folder_path = Path(docs_folder_str)
            docs_folder_path.mkdir(exist_ok=True)
            dbt_src_path = docs_folder_path / f"{src_name}.yml"
        else:
            dbt_src_path = (
                self.tmp_pkg_dir / "models" / self.models_subfolder / f"{src_name}.yml"
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

        db_errors_list = ["    " + error + "\n" for error in self.db_errors]
        db_errors_str = ""

        for db_error in db_errors_list:
            db_errors_str += db_error

        if self.db_errors:
            logger.info("")  # Terminal newline
            logger.warning(
                f"The following database error(s) were encountered "
                f"while templating the dbt package.\n"
                f"  NOTE - these errors do not prevent templating.\n\n{db_errors_str}"
            )

        logger.info(
            f"Copying dbt package from temporary path "
            f"{self.tmp_pkg_dir} to {self.dbt_pkg_dir}"
        )

        if self.dbt_pkg_dir.exists():
            shutil.rmtree(self.dbt_pkg_dir)

        shutil.copytree(self.tmp_pkg_dir, self.dbt_pkg_dir)

        logger.info("")  # Terminal newline
        logger.success(
            f"Modeled and documented tracking plan '{reflekt_plan.name}' "
            f"in dbt package '{self.dbt_package_name}'"
        )
        logger.info("")  # Terminal newline

    def _template_dbt_source(
        self,
        reflekt_plan: ReflektPlan,
    ) -> dict:
        logger.info(f"Initializing template for dbt source {self.schema}")
        src_name = (
            f"{self.src_prefix}{self.schema}"
            if self.schema_alias is None
            else f"{self.src_prefix}{self.schema_alias}"
        )

        if self.docs_in_folder:
            docs_folder_str = (
                str(self.tmp_pkg_dir) + f"/models/{self.models_subfolder}/docs"
            )
            docs_folder_path = Path(docs_folder_str)
            docs_folder_path.mkdir(exist_ok=True)
            dbt_src_path = docs_folder_path / f"{src_name}.yml"
        else:
            dbt_src_path = (
                self.tmp_pkg_dir / "models" / self.models_subfolder / f"{src_name}.yml"
            )

        if dbt_src_path.exists():
            with open(dbt_src_path, "r") as f:
                dbt_src = yaml.safe_load(f)

        else:
            dbt_src = copy.deepcopy(dbt_src_schema)
            dbt_src["sources"][0]["name"] = (
                self.schema_alias if self.schema_alias is not None else self.schema
            )
            dbt_src["sources"][0]["schema"] = self.schema
            dbt_src["sources"][0]["database"] = self.database
            dbt_src["sources"][0]["description"] = (
                f"Schema in {titleize(self.warehouse_type)} where raw event data for "
                f"the {reflekt_plan.name} tracking plan is loaded."
            )

        return dbt_src

    def _template_dbt_table(
        self,
        dbt_src: dict,
        table_name: str,
        table_description: str,
    ) -> None:
        # Get list of tables already in dbt source (if any)
        table_names = [dbt_tbl["name"] for dbt_tbl in dbt_src["sources"][0]["tables"]]

        # Table already defined in dbt source
        if table_name in table_names:
            logger.info("")  # Terminal newline
            logger.info(f"Templating table '{table_name}' in dbt source {self.schema}")

            for dbt_tbl in dbt_src["sources"][0]["tables"]:
                # Find existing table entry with matching name, update name & description
                if table_name == dbt_tbl["name"]:
                    dbt_tbl["name"] = table_name
                    dbt_tbl["description"] = table_description

        else:
            logger.info("")  # Terminal newline
            logger.info(f"Templating table '{table_name}' in dbt source {self.schema}")
            dbt_tbl = copy.deepcopy(dbt_table_schema)
            dbt_tbl["name"] = table_name
            dbt_tbl["description"] = table_description
            dbt_src["sources"][0]["tables"].append(dbt_tbl)

    def _template_dbt_model(
        self,
        models_subfolder: str,
        materialized: str,
        unique_key: str,
        table_name: str,
        model_name: str,
        db_columns: list,
        cdp_cols: dict,
        plan_cols: list,
        event_name: Optional[str] = None,
    ) -> None:
        logger.info("")  # Terminal newline
        logger.info(
            f"Templating dbt model "
            f"{self.model_prefix}{self.schema}__{table_name}.sql"
        )
        logger.info("    Adding {{ config(...) }} to model SQL")
        mdl_sql = self._template_dbt_model_config(
            table_name,
            materialized,
            unique_key,
            self.warehouse_type,
        )
        logger.info("    Adding source CTE to model SQL")
        source_schema = (
            self.schema_alias if self.schema_alias is not None else self.schema
        )
        mdl_sql += self._template_dbt_source_cte(
            source_schema=source_schema,
            source_table=table_name,
            incremental_logic=self.incremental_logic,
        )

        logger.info("    Adding renamed CTE to model SQL")
        mdl_sql += "renamed as (\n\n" "    select"

        for column, mapped_columns in cdp_cols.items():
            if column in db_columns or column in REFLEKT_TEMPLATE_COLUMNS:
                for mapped_column in mapped_columns:
                    if (
                        mapped_column["source_name"] in db_columns
                        or column in REFLEKT_TEMPLATE_COLUMNS
                    ) and mapped_column["schema_name"] is not None:
                        logger.info(
                            f"    Adding column '{mapped_column['schema_name']}' to "
                            f"model SQL"
                        )
                        col_sql = (
                            mapped_column["sql"]
                            .replace("__SCHEMA_NAME__", self.schema)
                            .replace("__TABLE_NAME__", table_name)
                            .replace("__PLAN_NAME__", self.plan_name)
                        )

                        if event_name is not None:
                            col_sql = col_sql.replace("__EVENT_NAME__", event_name)

                        mdl_sql += "\n        " + col_sql + ","

        for column in plan_cols:
            if (
                segment_2_snake(column.name) in db_columns
                and segment_2_snake(column.name) not in REFLEKT_RESERVED_COLUMNS
            ):
                # If the columns is named 'interval', surround in double quotes
                column_name = (
                    segment_2_snake(column.name)
                    if column.name != "interval"  # Handle columns named "interval"
                    else '"interval"'
                )
                logger.info(f"    Adding column '{column_name}' to model SQL")
                col_sql = column_name
                mdl_sql += "\n        " + col_sql + ","

        mdl_sql = mdl_sql[:-1]  # Remove final trailing comma
        # fmt: off
        mdl_sql += (
            "\n\n    from source"
            "\n\n)"
            "\n\n"
            "select * from renamed\n"
        )
        # fmt: on
        model_path = self.tmp_pkg_dir / "models" / models_subfolder / f"{model_name}.sql"

        with open(model_path, "w") as f:
            f.write(mdl_sql)

    def _template_dbt_model_config(
        self,
        table_name: str,
        materialized: str,
        unique_key: str,
        warehouse_type: str,
    ) -> str:
        if table_name in ["users", "groups"]:
            model_config = (
                "{{\n" "  config(\n" "    materialized = 'view',\n" "  )\n" "}}\n\n"
            )
        else:
            if materialized == "view":
                # fmt: off
                model_config = (
                    "{{\n"
                    "  config(\n"
                    "    materialized = 'view',\n"
                    "  )\n"
                    "}}\n\n"
                )
                # fmt: on
            elif materialized == "incremental":
                if warehouse_type == "redshift":
                    sort_str = "sort = 'tstamp'"
                elif warehouse_type == "snowflake":
                    sort_str = "cluster_by = 'tstamp'"
                model_config = (
                    "{{\n"
                    f"  config(\n"
                    f"    materialized = 'incremental',\n"
                    f"    unique_key = '{unique_key}',\n"
                    f"    {sort_str}\n"
                    f"  )\n"
                    "}}\n\n"
                )
            else:
                logger.error(
                    "Invalid 'materialized:' config in reflekt_project.yml. Must be "
                    "either 'view' or 'incremental'. See the Reflekt docs "
                    "(https://bit.ly/reflekt-project-config) on project configuration."
                )
                raise SystemExit(1)

        return model_config

    def _template_dbt_source_cte(
        self,
        source_schema: str,
        source_table: str,
        incremental_logic: Optional[str] = None,
    ) -> str:
        if incremental_logic is None:
            incremental_logic = ""

        # Format incremental_logic from reflekt_project.yml so it templates
        # according to dbt-labs style guide https://bit.ly/383kG7l
        incremental_logic_list = incremental_logic.splitlines()
        incremental_logic_str = ""
        for line in incremental_logic_list:
            incremental_logic_str += f"    {line}\n"

        source_cte = (
            "with\n\n"
            "source as (\n\n"
            f"    select *\n\n"
            f"    from {{{{ source('{underscore(source_schema)}', '{source_table}') }}}}\n"  # noqa: E501
            f"{incremental_logic_str}\n"
            "),\n\n"
        )

        return source_cte

    def _template_dbt_doc(
        self,
        models_subfolder: str,
        doc_name: str,
        model_name: str,
        model_description: str,
        db_columns: list,
        cdp_cols: dict,
        plan_cols: list,
    ) -> None:
        logger.info("")  # Terminal newline
        logger.info(
            f"Templating dbt docs " f"{doc_name}.yml" f" for model " f"{model_name}.sql"
        )
        dbt_doc = copy.deepcopy(dbt_doc_schema)
        dbt_mdl_doc = copy.deepcopy(dbt_model_schema)
        dbt_mdl_doc["name"] = model_name
        dbt_mdl_doc["description"] = model_description

        for column, mapped_columns in cdp_cols.items():
            if column in db_columns or column in REFLEKT_TEMPLATE_COLUMNS:
                for mapped_column in mapped_columns:
                    if mapped_column["schema_name"] is not None:
                        logger.info(
                            f"    Adding column '{mapped_column['schema_name']}' to "
                            f"dbt docs"
                        )
                        mdl_col = copy.deepcopy(dbt_column_schema)
                        mdl_col["name"] = mapped_column["schema_name"]
                        mdl_col["description"] = mapped_column["description"]
                        if mapped_column["source_name"] == "id" and (
                            self.docs_test_not_null or self.docs_test_unique
                        ):
                            mdl_col["tests"] = []

                            if self.docs_test_not_null:
                                mdl_col["tests"].append("not_null")

                            if self.docs_test_unique:
                                mdl_col["tests"].append("unique")

                        if mapped_column.get("tests") is not None:
                            mdl_col["tests"] = mapped_column["tests"]
                        dbt_mdl_doc["columns"].append(mdl_col)

        for column in plan_cols:
            if (
                segment_2_snake(column.name) in db_columns
                and segment_2_snake(column.name) not in REFLEKT_RESERVED_COLUMNS
            ):
                logger.info(
                    f"    Adding column '{segment_2_snake(column.name)}' to docs"
                )
                mdl_col = copy.deepcopy(dbt_column_schema)
                mdl_col["name"] = segment_2_snake(column.name)
                mdl_col["description"] = column.description
                dbt_mdl_doc["columns"].append(mdl_col)

        dbt_doc["models"].append(dbt_mdl_doc)

        if self.docs_in_folder:
            docs_folder_str = str(self.tmp_pkg_dir) + f"/models/{models_subfolder}/docs"
            docs_folder_path = Path(docs_folder_str)
            docs_folder_path.mkdir(exist_ok=True)
            docs_path = docs_folder_path / f"{doc_name}.yml"
        else:
            docs_path = (
                self.tmp_pkg_dir / "models" / models_subfolder / f"{doc_name}.yml"
            )

        with open(docs_path, "w") as f:
            yaml.dump(
                dbt_doc,
                f,
                indent=2,
                width=70,
                Dumper=ReflektYamlDumper,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
                encoding=("utf-8"),
            )
