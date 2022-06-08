# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import copy
import shutil
from typing import Optional, Union

import pkg_resources
import yaml
from inflection import titleize, underscore
from loguru import logger
from packaging.version import Version

from reflekt.reflekt.columns import reflekt_columns
from reflekt.reflekt.config import ReflektConfig
from reflekt.reflekt.dbt import (
    dbt_column_schema,
    dbt_doc_schema,
    dbt_model_schema,
    dbt_src_schema,
    dbt_table_schema,
)
from reflekt.reflekt.dumper import ReflektYamlDumper
from reflekt.reflekt.errors import ReflektProjectError
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
        # database: Optional[str] = None,
        # schema: Optional[str] = None,
        dbt_package_name: Optional[str] = None,
        pkg_version: Optional[Version] = None,
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
            self.dbt_package_name = dbt_package_name
            self.tmp_pkg_dir = (
                self.project_dir / ".reflekt" / "tmp" / self.dbt_package_name
            )
            self.dbt_pkgs_dir = self.project_dir / "dbt_packages"
            self.dbt_pkg_path = self.dbt_pkgs_dir / self.dbt_package_name
            self.pkg_template = pkg_resources.resource_filename(
                "reflekt", "templates/dbt/"
            )
            self.pkg_version = pkg_version
            self.db_engine = WarehouseConnection()
            self.src_prefix = self.reflekt_project.src_prefix
            self.model_prefix = self.reflekt_project.model_prefix
            self.docs_prefix = self.reflekt_project.docs_prefix
            self.materialized = self.reflekt_project.materialized
            self.incremental_logic = self.reflekt_project.incremental_logic

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
        print("")  # Terminal newline
        logger.info(
            f"Converting Reflekt tracking plan '{self.plan_name}'to "
            f"{titleize(self.plan_type)} format"
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
        # NOTE - ReflektTrait is a child class of ReflektProperty, so this
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
        logger.info(
            f"Building Reflekt dbt package:"
            f"\n        cdp: {self.cdp_name}"
            f"\n        analytics governance tool: {self.plan_type}"
            f"\n        tracking plan: {self.plan_name}"
            f"\n        warehouse: {self.warehouse_type}"
            f"\n        schema: {self.schema}"
            f"\n        schema_alias: {self.schema_alias}"
            f"\n        dbt package name: {self.dbt_package_name}"
            f"\n        dbt package version: {self.pkg_version}"
            f"\n        dbt package path: {self.dbt_pkg_path}\n"
        )

        if self.tmp_pkg_dir.exists():
            shutil.rmtree(str(self.tmp_pkg_dir))
        shutil.copytree(self.pkg_template, str(self.tmp_pkg_dir))

        # Update the version string in templated dbt_project.yml
        with open(self.tmp_pkg_dir / "dbt_project.yml", "r") as f:
            dbt_project_yml_str = f.read()

        dbt_project_yml_str = dbt_project_yml_str.replace(
            "0.1.0", str(self.pkg_version)  # Template always has version '0.1.0'
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

        if self.cdp_name == "rudderstack":
            return self._dbt_package_rudderstack(self.reflekt_plan)
        elif self.cdp_name == "segment":
            return self._dbt_package_segment(self.reflekt_plan)
        elif self.cdp_name == "snowplow":
            return self._dbt_package_snowplow(self.reflekt_plan)

    def _dbt_package_rudderstack(self):
        pass

    def _dbt_package_snowplow(self):
        pass

    def _dbt_package_segment(self, reflekt_plan: ReflektPlan) -> None:
        self.db_errors = []

        # Setup `Page Viewed` and `Screen Viewed` events, if they exist in Reflekt plan
        page_viewed_event = [
            event
            for event in reflekt_plan.events
            if str.lower(event.name).replace("_", " ").replace("-", " ") == "page viewed"
        ]

        if page_viewed_event == []:  # Page Viewed not in tracking plan
            page_viewed_props = []
        else:
            page_viewed_props = page_viewed_event[0].properties

        screen_viewed_event = [
            event
            for event in reflekt_plan.events
            if str.lower(event.name).replace("_", " ").replace("-", " ")
            == "screen viewed"
        ]

        if screen_viewed_event == []:  # Screen Viewed not in tracking plan
            screen_viewed_props = []
        else:
            screen_viewed_props = screen_viewed_event[0].properties

        std_segment_tables = [
            {
                "name": "identifies",
                "description": "A table with identify() calls.",  # noqa: E501
                "unique_key": "identify_id",
                "cdp_cols": seg_identify_cols,
                "plan_cols": [],
            },
            {
                "name": "users",
                "description": "A table with the latest traits for users.",  # noqa: E501
                "unique_key": "user_id",
                "cdp_cols": seg_users_cols,
                "plan_cols": [],
            },
            {
                "name": "groups",
                "description": "A table with group() calls.",  # noqa: E501
                "unique_key": "group_id",
                "cdp_cols": seg_groups_cols,
                "plan_cols": [],
            },
            {
                "name": "pages",
                "description": "A table with page() calls.",  # noqa: E501
                "unique_key": "page_id",
                "cdp_cols": seg_pages_cols,
                "plan_cols": page_viewed_props,
            },
            {
                "name": "screens",
                "description": "A table with screen() calls.",  # noqa: E501
                "unique_key": "screen_id",
                "cdp_cols": seg_screens_cols,
                "plan_cols": screen_viewed_props,
            },
            {
                "name": "tracks",
                "description": "A table with track() event calls.",  # noqa: E501
                "unique_key": "event_id",
                "cdp_cols": seg_tracks_cols,
                "plan_cols": [],
            },
        ]

        dbt_src = self._template_dbt_source(reflekt_plan=reflekt_plan)

        for std_segment_table in std_segment_tables:
            if self.plan_type == "avo" and std_segment_table["name"] in [
                "identifies",
                "users",
                "groups",
            ]:
                pass
            else:
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
                        materialized=self.materialized,
                        unique_key=std_segment_table["unique_key"],
                        table_name=table_name,
                        model_name=model_name,
                        db_columns=db_columns,
                        cdp_cols=std_segment_table["cdp_cols"],
                        plan_cols=std_segment_table["plan_cols"],
                    )
                    self._template_dbt_doc(
                        doc_name=doc_name,
                        model_name=model_name,
                        model_description=std_segment_table["description"],
                        db_columns=db_columns,
                        cdp_cols=std_segment_table["cdp_cols"],
                        plan_cols=std_segment_table["plan_cols"],
                    )

        for event in reflekt_plan.events:
            if event.name.lower() in ["page viewed", "screen viewed"]:
                pass  # Already handled above by std_segment_tables for loop
            else:
                db_columns, error_msg = self.db_engine.get_columns(
                    self.schema, segment_2_snake(event.name)
                )
                if error_msg is not None:
                    self.db_errors.append(error_msg)
                else:
                    table_name = segment_2_snake(event.name)
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
                        materialized=self.materialized,
                        unique_key="event_id",
                        table_name=table_name,
                        model_name=model_name,
                        db_columns=db_columns,
                        cdp_cols=seg_event_cols,
                        plan_cols=event.properties,
                    )
                    self._template_dbt_doc(
                        doc_name=doc_name,
                        model_name=model_name,
                        model_description=event.description,
                        db_columns=db_columns,
                        cdp_cols=seg_event_cols,
                        plan_cols=event.properties,
                    )

        src_name = (
            f"{self.src_prefix}{self.schema}"
            if self.schema_alias is None
            else f"{self.src_prefix}{self.schema_alias}"
        )
        dbt_src_path = self.tmp_pkg_dir / "models" / f"{src_name}.yml"

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
            print("")  # Terminal newline
            logger.warning(
                f"[WARNING] The following database error(s) were encountered "
                f"while templating the dbt package. NOTE - these errors do not prevent "
                f"templating.\n\n{db_errors_str}"
            )

        logger.info(
            f"Copying dbt package from temporary path "
            f"{self.tmp_pkg_dir} to {self.dbt_pkg_path}"
        )

        if self.dbt_pkg_path.exists():
            shutil.rmtree(self.dbt_pkg_path)

        shutil.copytree(self.tmp_pkg_dir, self.dbt_pkg_path)

        print("")  # Terminal newline
        logger.info(
            f"[SUCCESS] Created Reflekt dbt package '{self.dbt_package_name}' "
            f"at: {self.dbt_pkg_path}"
        )
        print("")  # Cleanup stdout

    def _template_dbt_source(self, reflekt_plan: ReflektPlan) -> dict:
        logger.info(f"Initializing template for dbt source {self.schema}")
        dbt_src = copy.deepcopy(dbt_src_schema)
        dbt_src["sources"][0]["name"] = (
            self.schema_alias if self.schema_alias is not None else self.schema
        )
        dbt_src["sources"][0]["schema"] = self.schema
        dbt_src["sources"][0]["database"] = self.database
        dbt_src["sources"][0]["description"] = (
            f"Schema in {titleize(self.warehouse_type)} where data for the "
            f"{reflekt_plan.name} {titleize(self.cdp_name)} source is stored."
        )

        return dbt_src

    def _template_dbt_table(
        self,
        dbt_src: dict,
        table_name: str,
        table_description: str,
        # db_columns: list,
        # cdp_cols: dict,
        # plan_cols: list,
    ) -> None:
        print("")  # Terminal newline
        logger.info(f"Templating table '{table_name}' in dbt source {self.schema}")
        dbt_tbl = copy.deepcopy(dbt_table_schema)
        dbt_tbl["name"] = table_name
        dbt_tbl["description"] = table_description
        dbt_src["sources"][0]["tables"].append(dbt_tbl)

    def _template_dbt_model(
        self,
        materialized: str,
        unique_key: str,
        table_name: str,
        model_name: str,
        db_columns: list,
        cdp_cols: dict,
        plan_cols: list,
    ) -> None:
        print("")  # Terminal newline
        logger.info(
            f"Templating dbt model "
            f"{self.model_prefix}{self.schema}__{table_name}.sql"
        )
        logger.info("    Adding {{ config(...) }} to model SQL")
        mdl_sql = self._template_dbt_model_config(
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
            if column in db_columns or column in reflekt_columns:
                for mapped_column in mapped_columns:
                    if mapped_column["schema_name"] is not None:
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
                        mdl_sql += "\n        " + col_sql + ","

        for column in plan_cols:
            logger.info(
                f"    Adding column '{segment_2_snake(column.name)}' to model SQL"
            )
            col_sql = segment_2_snake(column.name)
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
        model_path = self.tmp_pkg_dir / "models" / f"{model_name}.sql"

        with open(model_path, "w") as f:
            f.write(mdl_sql)

    def _template_dbt_model_config(
        self,
        materialized: str,
        unique_key: str,
        warehouse_type: str,
    ) -> str:
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
            raise ReflektProjectError(
                f"Invalid materialized config in reflekt_project.yml...\n"
                f"    materialized: {materialized}\n"
                f"... is not accepted. Must be either 'view' or 'incremental'."
            )

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
        doc_name: str,
        model_name: str,
        model_description: str,
        db_columns: list,
        cdp_cols: dict,
        plan_cols: list,
    ) -> None:
        print("")  # Terminal newline
        logger.info(
            f"Templating dbt docs " f"{doc_name}.yml" f" for model " f"{model_name}.sql"
        )
        dbt_doc = copy.deepcopy(dbt_doc_schema)
        dbt_mdl_doc = copy.deepcopy(dbt_model_schema)
        dbt_mdl_doc["name"] = model_name
        dbt_mdl_doc["description"] = model_description

        for column, mapped_columns in cdp_cols.items():
            if column in db_columns or column in reflekt_columns:
                for mapped_column in mapped_columns:
                    if mapped_column["schema_name"] is not None:
                        logger.info(
                            f"    Adding column '{mapped_column['schema_name']}' to "
                            f"dbt docs"
                        )
                        mdl_col = copy.deepcopy(dbt_column_schema)
                        mdl_col["name"] = mapped_column["schema_name"]
                        mdl_col["description"] = mapped_column["description"]
                        if mapped_column.get("tests") is not None:
                            mdl_col["tests"] = mapped_column["tests"]
                        dbt_mdl_doc["columns"].append(mdl_col)

        for column in plan_cols:
            logger.info(f"    Adding column '{segment_2_snake(column.name)}' to docs")
            mdl_col = copy.deepcopy(dbt_column_schema)
            mdl_col["name"] = segment_2_snake(column.name)
            mdl_col["description"] = column.description
            dbt_mdl_doc["columns"].append(mdl_col)

        dbt_doc["models"].append(dbt_mdl_doc)

        docs_path = self.tmp_pkg_dir / "models" / f"{doc_name}.yml"

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
