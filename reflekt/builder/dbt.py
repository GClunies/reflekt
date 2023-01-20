# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import shutil
from pathlib import Path
from typing import Dict, List

import pkg_resources
import yaml
from inflection import titleize, underscore
from loguru import logger
from rich import print

from reflekt.dumper import ReflektYamlDumper
from reflekt.flatson import Flatson
from reflekt.project import Project
from reflekt.warehouse import Warehouse


class DbtBuilder:
    """dbt builder class.

    Builds a dbt package for specified set of schemas.
    """

    def __init__(
        self,
        select: str,
        schema_paths: List[Path],
        sdk: str,
        target: str,
    ) -> None:
        """Initialize dbt builder class.

        Args:
            select (str): The --select argument passed to Reflekt CLI.
            schema_paths (List[Path]): List of schema paths to build.
            sdk (str): The --sdk argument passed to Reflekt CLI.
            target (str): The --target argument passed to Reflekt CLI.
        """

        self._project = Project()
        self._pkg_name = self._project.name
        self._pkg_dir = self._project.dir / "artifacts" / "dbt" / self._pkg_name
        self._tmp_pkg_dir = (
            self._project.dir / ".reflekt_cache" / "artifacts" / "dbt" / self._pkg_name
        )
        self._blank_dbt_pkg = pkg_resources.resource_filename(
            "reflekt", "_templates/dbt_package/"
        )
        self._src_prefix = self._project.artifacts["dbt"]["sources"]["prefix"]
        self._mdl_prefix = self._project.artifacts["dbt"]["models"]["prefix"]
        # self._mdl_materialized = self._project.artifacts["dbt"]["models"][
        #     "materialized"
        # ]
        # self._mdl_where = self._project.artifacts["dbt"]["models"]["where"]
        self._doc_prefix = self._project.artifacts["dbt"]["docs"]["prefix"]
        self._doc_folder = self._project.artifacts["dbt"]["docs"]["in_folder"]
        self._doc_folder_str = "" if not self._doc_folder else "docs/"
        # self._test_not_null = self._project.artifacts["dbt"]["docs"]["test_not_null"]
        # self._test_unique = self._project.artifacts["dbt"]["docs"]["test_unique"]
        self.wh_errors = []
        self._select = select
        self._schema_paths = schema_paths
        self._sdk = sdk
        self._target = target
        self._warehouse = Warehouse(self._target)
        self._warehouse_type = self._warehouse.type
        self._database = self._warehouse.database
        self._schema = self._warehouse.schema

    def _build_dbt_source(self) -> Dict:
        """Build dbt source.

        Returns:
            Dict: dbt source object.
        """
        src_path = (
            self._tmp_pkg_dir
            / "models"
            / self._doc_folder_str
            / f"{self._src_prefix}{self._schema}.yml"
        )

        # If source already exists in temp dbt pkg (copied from existing pkg), use it
        if src_path.exists():
            with src_path.open("r") as f:
                dbt_source = yaml.safe_load(f)
        else:
            dbt_source = {
                "version": 2,
                "sources": [
                    {
                        "name": self._schema,
                        "schema": self._schema,
                        "database": self._database,
                        "description": f"Schema in {self._warehouse_type} with raw {titleize(self._sdk)} event data.",  # noqa: E501
                        "tables": [],
                    }
                ],
            }

        logger.info(f"Building dbt source '{self._schema}'")

        return dbt_source

    def _build_dbt_table(self, source: Dict, table_name: str, description: str) -> None:
        """Build dbt table.

        Args:
            source (Dict): dbt source object.
            table_name (str): Table name.
            description (str): Table description.
        """
        dbt_table = {"name": table_name, "description": description}
        source["sources"][0]["tables"].append(dbt_table)
        logger.info(f"Building dbt table '{table_name}' in source '{self._schema}'")

    def _build_dbt_model(self, table_name: str, columns: List[Dict]) -> None:
        """Build dbt model.

        Args:
            table_name (str): Table name.
            columns (List[Dict]): List of column dicts (with name, description, etc).
        """
        model_file: str = f"{self._mdl_prefix}{self._schema}__{table_name}.sql"
        model_path: Path = self._tmp_pkg_dir / "models" / self._schema / model_file
        mdl_sql = (  # Config
            "{{\n"
            "  config(\n"
            "    materialized = 'view'\n"  # noqa: E501
            "  )\n"
            "}}\n\n"
        )
        mdl_sql += (  # Import CTE
            f"with\n\n"
            f"source as (\n"
            f"    select * from {{{{ source('{underscore(self._schema)}', '{table_name}') }}}}\n"  # noqa: E501
            f"),\n\n"
        )
        mdl_sql += "renamed as (\n" "    select"  # Rename CTE

        if self._sdk == "segment":
            for col in columns:
                col_name = underscore(col["name"])

                if col_name == "id":
                    if table_name == "identifies":
                        col_sql = f"\n        {col_name} as identify_id,"
                    elif table_name == "users":
                        col_sql = f"\n        {col_name} as user_id,"
                    elif table_name == "groups":
                        col_sql = f"\n        {col_name} as group_id,"
                    elif table_name == "pages":
                        col_sql = f"\n        {col_name} as page_id,"
                    elif table_name == "screens":
                        col_sql = f"\n        {col_name} as screen_id,"
                    elif table_name == "tracks":
                        col_sql = f"\n        {col_name} as event_id,"
                    else:  # Custom events
                        col_sql = f"\n        {col_name} as event_id,"
                elif col_name in [
                    "original_timestamp",
                    "sent_at",
                    "received_at",
                    "timestamp",
                ]:
                    alias_name = col_name.replace("timestamp", "tstamp").replace(
                        "_at", "_at_tstamp"
                    )
                    col_sql = f"\n        {col_name} as {alias_name},"
                elif "context_" in col_name:
                    alias_name = f"{col_name.replace('context_', '')},"
                    col_sql = f"\n        {col_name} as {alias_name}"
                else:
                    col_sql = f"\n        {col_name},"

                mdl_sql += col_sql

        mdl_sql = mdl_sql[:-1]  # Remove final trailing comma
        mdl_sql += "\n    from source\n)\n\nselect * from renamed"

        if not model_path.parent.exists():
            model_path.parent.mkdir(parents=True)

        with model_path.open("w+") as f:
            f.write(mdl_sql)

        logger.info(f"Building staging model '{model_file}'")

    def _build_dbt_metric(self) -> None:
        """Build dbt metric."""
        pass  # TODO - reserved for later use

    def _build_dbt_doc(
        self, table_name: str, description: str, columns: List[Dict]
    ) -> None:
        """Build dbt documentation for model.

        Args:
            table_name (str): Table name.
            description (str): Model description.
            columns (List[Dict]): List of column dicts (with name, description, etc).
        """
        doc_file = f"{self._doc_prefix}{self._schema}__{table_name}.yml"
        doc_path = (
            self._tmp_pkg_dir
            / "models"
            / self._schema
            / self._doc_folder_str
            / doc_file
        )
        doc_obj = {
            "version": 2,
            "models": [
                {
                    "name": table_name,
                    "description": description,
                    "columns": [],
                }
            ],
        }
        test_cols = list(self._project.artifacts["dbt"]["docs"]["tests"].keys())

        for col in columns:
            if col["name"] == "id":
                if table_name == "identifies":
                    col_name = "identify_id"
                elif table_name == "users":
                    col_name = "user_id"
                elif table_name == "groups":
                    col_name = "group_id"
                elif table_name == "pages":
                    col_name = "page_id"
                elif table_name == "screens":
                    col_name = "screen_id"
                elif table_name == "tracks":
                    col_name = "event_id"
                else:  # Custom events
                    col_name = "event_id"
            else:
                col_name = (
                    underscore(col["name"])
                    .replace("timestamp", "tstamp")
                    .replace("_at", "_at_tstamp")
                    if "context_" not in underscore(col["name"])
                    else underscore(col["name"]).replace("context_", "")
                )

            dbt_col = {
                "name": col_name,
                "description": col["description"],
            }

            if col["name"] in test_cols:
                dbt_col["tests"] = self._project.artifacts["dbt"]["docs"]["tests"][
                    col["name"]
                ]

            doc_obj["models"][0]["columns"].append(dbt_col)

        with doc_path.open("w") as f:
            yaml.dump(
                doc_obj,
                f,
                indent=2,
                width=70,
                Dumper=ReflektYamlDumper,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
                encoding=("utf-8"),
            )

        logger.info(f"Building dbt documentation '{doc_file}'")

    def build(self) -> None:
        """Build dbt package."""
        print("")
        logger.info(
            f"Building dbt package:"
            f"\n    name: {self._pkg_name}"
            f"\n    dir: {self._pkg_dir}"
            f"\n    --select: {self._select}"
            f"\n    --sdk: {self._sdk}"
            f"\n    --target: {self._target}"
        )
        print("")

        if self._pkg_dir.exists():  # If dbt pkg exists, use as base for build
            if self._tmp_pkg_dir.exists():  # Start temp pkg blank template
                shutil.rmtree(self._tmp_pkg_dir)
            shutil.copytree(self._pkg_dir, self._tmp_pkg_dir)
        else:  # If dbt pkg does not exist, temp pkg from blank template
            if self._tmp_pkg_dir.exists():
                shutil.rmtree(self._tmp_pkg_dir)
            shutil.copytree(
                self._blank_dbt_pkg, str(self._tmp_pkg_dir), dirs_exist_ok=True
            )

        # Update dbt_project.yml
        with open(self._tmp_pkg_dir / "dbt_project.yml", "r") as f:
            dbt_project_yml = f.read()

        dbt_project_yml = dbt_project_yml.replace("package_name", self._pkg_name)

        with open(self._tmp_pkg_dir / "dbt_project.yml", "w") as f:
            f.write(dbt_project_yml)

        # Update README.md
        with open(self._tmp_pkg_dir / "README.md", "r") as f:
            readme_md = f.read()

        readme_md = readme_md.replace("_DBT_PKG_NAME_", self._pkg_name)

        with open(self._tmp_pkg_dir / "README.md", "w") as f:
            f.write(readme_md)

        source_obj = self._build_dbt_source()
        source_path = (
            self._tmp_pkg_dir
            / "models"
            / self._schema
            / self._doc_folder_str
            / f"{self._src_prefix}{self._schema}.yml"
        )

        # Get common columns based on SDK used to collect event data
        if self._sdk == "segment":
            common_json = (
                self._project.dir
                / "schemas"
                / ".reflekt"
                / "segment"
                / "common"
                / "1-0.json"
            )
        # elif self._sdk == "rudderstack":
        #     pass
        # elif self._sdk == "snowplow":
        #     pass
        # elif self._sdk == "amplitude":
        #     pass

        common_columns = [
            {
                "name": underscore(
                    field.name.replace("messageId", "id").replace(".", "_")
                ),
                "description": field.schema["description"],
            }
            for field in Flatson.from_schemafile(common_json).fields
        ]

        # Iterate through all schemas to build artifacts
        for schema_path in self._schema_paths:
            # Get schema name and version
            schema_name = schema_path.parts[-2]
            schema_version = int(schema_path.parts[-1].split(".")[0].replace("-", ""))
            # Get all schemas with same name, then get versions of those schemas
            schema_paths_same_name = [
                p for p in self._schema_paths if p.parts[-2] == schema_name
            ]
            schema_versions = [
                int(schema_path.name.split("/")[-1].split(".")[0].replace("-", ""))
                for schema_path in schema_paths_same_name
            ]

            # Only build table/model/doc for the LATEST schema version
            if schema_version == max(schema_versions):
                logger.info(f"Building dbt artifacts for schema: {schema_path}")
                # Get event schema details
                with schema_path.open("r") as f:
                    schema_json = json.load(f)

                event_name = schema_json["self"]["name"]
                event_desc = schema_json["description"]
                table_name = underscore(event_name.lower().replace(" ", "_"))

                if self._sdk == "segment":
                    table_name = (
                        table_name.replace("identify", "identifies")
                        .replace("group", "groups")
                        .replace("page_viewed", "pages")
                        .replace("screen_viewed", "screens")
                    )

                schema_columns = [
                    {
                        "name": underscore(field.name.replace(".", "_")),
                        "description": field.schema["description"],
                    }
                    for field in Flatson.from_schemafile(schema_path).fields
                ]
                all_columns = common_columns + schema_columns
                warehouse_columns, warehouse_error = self._warehouse.get_columns(
                    table=table_name
                )

                if warehouse_error is not None:
                    self.wh_errors.append(warehouse_error)
                else:
                    columns = [
                        col for col in all_columns if col["name"] in warehouse_columns
                    ]
                    self._build_dbt_table(
                        source=source_obj,
                        table_name=table_name,
                        description=event_desc,
                    )
                    self._build_dbt_model(
                        table_name=table_name,
                        columns=columns,
                    )
                    self._build_dbt_doc(
                        table_name=table_name,
                        description=event_desc,
                        columns=columns,
                    )

                    if self._sdk == "segment" and table_name == "identifies":
                        # Build Segment users table/model/doc
                        self._build_dbt_table(
                            source=source_obj,
                            table_name="users",
                            description="User traits set by identify() calls.",
                        )
                        self._build_dbt_model(
                            table_name="users",
                            columns=columns,
                        )
                        self._build_dbt_doc(
                            table_name="users",
                            description="User traits set by identify() calls.",
                            columns=columns,
                        )

        if self._sdk == "segment":
            # Build Segment users table/model/doc
            self._build_dbt_table(
                source=source_obj,
                table_name="tracks",
                description=(
                    "A summary of track() calls from all events. Properties unique "
                    "to each event's track() call are omitted."
                ),
            )
            self._build_dbt_model(
                table_name="tracks",
                columns=common_columns,
            )
            self._build_dbt_doc(
                table_name="tracks",
                description=(
                    "A summary of track() calls from all events. Properties unique "
                    "to each event's track() call are omitted."
                ),
                columns=common_columns,
            )

        with source_path.open("w") as f:
            yaml.dump(
                source_obj,
                f,
                indent=2,
                width=70,
                Dumper=ReflektYamlDumper,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
                encoding=("utf-8"),
            )

        wh_errors_list = [error + "\n" for error in self.wh_errors]
        wh_errors_str = ""

        for wh_error in wh_errors_list:
            wh_errors_str += wh_error

        if self.wh_errors:
            print("")
            logger.warning(
                f"The following data warehouse error(s) occurred while building "
                f"the dbt package. NOTE - 'Object ... does not exist' errors are "
                f"expected for schemas that have not produced data at the specified "
                f"'--target'. These errors DO NOT prevent successful package build. "
                f"\n\n{wh_errors_str}"
            )

        logger.info(
            f"Copying dbt package from temporary path "
            f"{self._tmp_pkg_dir} to {self._pkg_dir}"
        )

        if self._pkg_dir.exists():
            shutil.rmtree(self._pkg_dir)

        shutil.copytree(self._tmp_pkg_dir, self._pkg_dir)

        print("")
        logger.info("[green]Successfully built dbt package[green/]")
