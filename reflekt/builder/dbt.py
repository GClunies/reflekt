# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

import pkg_resources
import yaml
from inflection import titleize, underscore
from loguru import logger
from rich import print

from reflekt.dumper import ReflektYamlDumper
from reflekt.flatson import Flatson
from reflekt.profile import Profile
from reflekt.project import Project
from reflekt.warehouse import Warehouse


class DbtBuilder:
    """dbt builder class.

    Builds a dbt package for specified set of schemas.
    """

    def __init__(
        self,
        select_arg: str,
        schema_paths: List[Path],
        sdk_arg: str,
        source_arg: str,
        profile: Profile,
    ) -> None:
        """Initialize dbt builder class.

        Args:
            select_arg (str): The --select argument passed to Reflekt CLI.
            schema_paths (List[Path]): List of schema paths to build.
            sdk_arg (str): The --sdk argument passed to Reflekt CLI.
            source_arg (str): The --source argument passed to Reflekt CLI.
            profile (Profile): Reflekt Profile object.
        """
        self._profile = profile
        self._project = Project()
        self._pkg_name = underscore(self._project.name)
        self._pkg_dir = self._project.dir / "artifacts" / "dbt" / self._pkg_name
        self._tmp_pkg_dir = (
            self._project.dir / ".reflekt_cache" / "artifacts" / "dbt" / self._pkg_name
        )
        self._blank_dbt_pkg = pkg_resources.resource_filename(
            "reflekt", "_templates/dbt_package/"
        )
        self._src_prefix = self._project.artifacts["dbt"]["sources"]["prefix"]
        self._mdl_prefix = self._project.artifacts["dbt"]["models"]["prefix"]
        self._doc_prefix = self._project.artifacts["dbt"]["docs"]["prefix"]
        self._doc_folder = self._project.artifacts["dbt"]["docs"]["in_folder"]
        self._doc_folder_str = "" if not self._doc_folder else "docs/"
        self.wh_errors = []
        self._select_arg = select_arg
        self._schema_paths = schema_paths
        self._sdk_arg = sdk_arg
        self._source_arg = source_arg
        self._warehouse = Warehouse(source_arg=self._source_arg, profile=self._profile)
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

        # If dbt source exists in temp dbt pkg (copied from existing pkg), use it
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
                        "description": f"Schema in {self._warehouse_type} with raw {titleize(self._sdk_arg)} event data.",  # noqa: E501
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
        # Find existing tables in dbt source
        existing_tables = [t["name"] for t in source["sources"][0]["tables"]]

        if table_name not in existing_tables:
            source["sources"][0]["tables"].append(dbt_table)
            logger.info(f"Building dbt table '{table_name}' in source '{self._schema}'")

    def _build_dbt_model(
        self,
        schema_id: str,
        source_schema: str,
        table_name: str,
        columns: List[Dict],
        metadata: Dict,
        filter: Optional[str] = None,
    ) -> None:
        """Build dbt model.

        Args:
            schema_id (str): Reflekt schema ID.
            source_schema (str): source schema.
            table_name (str): Table name.
            columns (List[Dict]): List of column dicts (with name, description, etc).
            metadata (Dict): Schema metadata.
            filter (Optional[str]): Filter to apply to model. Defaults to None.
        """
        schema_version = underscore(schema_id.split("/")[-1].replace(".json", ""))
        model_file = (
            f"{self._mdl_prefix}{self._schema}__{table_name}__v{schema_version}.sql"
            if schema_version != "1_0"
            else f"{self._mdl_prefix}{self._schema}__{table_name}.sql"
        )
        model_path: Path = self._tmp_pkg_dir / "models" / self._schema / model_file
        mdl_sql = (  # Config
            "{{\n"
            "  config(\n"
            "    materialized = 'view'\n"  # noqa: E501
            "  )\n"
            "}}\n\n"
        )
        mdl_sql += (  # Import CTE start
            f"with\n\n"
            f"source as (\n"
            f"    select *\n"
            f"    from {{{{ source('{underscore(self._schema)}', '{table_name}') }}}}\n"
        )

        # Add filter to SQL if provided and table is not an entity table
        if filter is not None:
            if self._sdk_arg == "segment" and table_name not in ["users", "groups"]:
                filter_list = self._project.artifacts["dbt"]["models"][
                    "filter"
                ].splitlines()
                filter_str = ""

                for line in filter_list:
                    filter_str += f"    {line}\n"
        else:
            filter_str = ""

        mdl_sql += f"{filter_str}),\n\n"  # Import CTE end
        mdl_sql += "renamed as (\n" "    select"  # Rename CTE start

        if self._sdk_arg == "segment":  # TODO - should this be its own method?
            taken_cols = []  # Used to check for duplicates

            for col in columns:
                col_name = underscore(col["name"])

                # Rename columns for staging models
                if col_name == "id":  # ID column
                    if table_name == "identifies":
                        alias_name = "identify_id"
                        taken_cols.append(alias_name)
                        col_sql = f"\n        {col_name} as {alias_name},"
                    elif table_name == "users":
                        alias_name = "user_id"
                        taken_cols.append(alias_name)
                        col_sql = f"\n        {col_name} as {alias_name},"
                    elif table_name == "groups":
                        alias_name = "group_id"
                        taken_cols.append(alias_name)
                        col_sql = f"\n        {col_name} as {alias_name},"
                    elif table_name == "pages":
                        alias_name = "page_id"
                        taken_cols.append(alias_name)
                        col_sql = f"\n        {col_name} as {alias_name},"
                    elif table_name == "screens":
                        alias_name = "screen_id"
                        taken_cols.append(alias_name)
                        col_sql = f"\n        {col_name} as {alias_name},"
                    else:  # 'tracks' table and custom events
                        alias_name = "event_id"
                        taken_cols.append(alias_name)
                        col_sql = f"\n        {col_name} as {alias_name},"
                elif col_name == "event_text":  # Event name column
                    alias_name = "event_name"
                    taken_cols.append(alias_name)
                    col_sql = f"\n        {col_name} as {alias_name},"
                elif col_name in [  # Timestamp columns
                    "original_timestamp",
                    "sent_at",
                    "received_at",
                    "timestamp",
                ]:
                    alias_name = col_name.replace("timestamp", "tstamp").replace(
                        "_at", "_at_tstamp"
                    )
                    taken_cols.append(alias_name)
                    col_sql = f"\n        {col_name} as {alias_name},"
                elif "context_" in col_name:  # Context columns
                    alias_name = f"{col_name.replace('context_', '')},"
                    taken_cols.append(alias_name)
                    col_sql = f"\n        {col_name} as {alias_name}"
                else:  # Other columns (i.e., from schema properties)
                    col_sql = (  # Rename column from schema, check for duplicate names
                        f"\n        {col_name},"
                        if col_name not in taken_cols
                        and col_name
                        not in [  # These columns are added to the model later
                            "call_type",
                            "source_schema",
                            "source_table",
                            "schema_id",
                        ]
                        else f"\n        _{col_name},"
                    )

                mdl_sql += col_sql  # Add column to SQL

            # Columns to describe the Segment call type and where the data came from
            if table_name in ["identifies", "users"]:
                alias_name = "call_type"
                taken_cols.append(alias_name)
                col_sql = f"\n        'identify'::varchar as {alias_name},"
            elif table_name == "groups":
                alias_name = "call_type"
                taken_cols.append(alias_name)
                col_sql = f"\n        'group'::varchar as {alias_name},"
            elif table_name == "pages":
                alias_name = "call_type"
                taken_cols.append(alias_name)
                col_sql = f"\n        'page'::varchar as {alias_name},"
            elif table_name == "screens":
                alias_name = "call_type"
                taken_cols.append(alias_name)
                col_sql = f"\n        'screen'::varchar as {alias_name},"
            else:
                alias_name = "call_type"
                taken_cols.append(alias_name)
                col_sql = f"\n        'track'::varchar as {alias_name},"

            mdl_sql += col_sql  # Add call_type column
            mdl_sql += (  # Add columns for data source and schema ID
                f"\n        '{source_schema}'::varchar as source_schema,"
                f"\n        '{table_name}'::varchar as source_table,"
                f"\n        '{schema_id}'::varchar as schema_id,"
            )
            taken_cols.extend(["source_schema", "source_table", "schema_id"])

            if metadata != {}:  # Add metadata columns
                metadata_str = json.dumps(metadata)
                alias_name = "schema_metadata"
                taken_cols.append(alias_name)
                col_sql = f"\n        '{metadata_str}'::varchar as {alias_name},"
                mdl_sql += col_sql

        mdl_sql = mdl_sql[:-1]  # Remove final trailing comma from last rename
        mdl_sql += "\n    from source\n)"  # Rename CTE end
        mdl_sql += "\n\nselect * from renamed"  # Final select

        if not model_path.parent.exists():
            model_path.parent.mkdir(parents=True)

        with model_path.open("w+") as f:
            f.write(mdl_sql)

        logger.info(f"Building staging model '{model_file}'")

    # def _build_dbt_metric(self) -> None:  # TODO - reserved for later use
    #     """Build dbt metric."""
    #     pass

    def _build_dbt_doc(
        self,
        schema_id: str,
        table_name: str,
        description: str,
        columns: List[Dict],
        metadata: Dict,
    ) -> None:
        """Build dbt documentation for model.

        Args:
            schema_id (str): Reflekt schema ID.
            table_name (str): Table name.
            description (str): Model description.
            columns (List[Dict]): List of column dicts (with name, description, etc).
            metadata (Dict): Schema metadata.
        """
        schema_version = underscore(schema_id.split("/")[-1].replace(".json", ""))
        model_name = (
            f"{self._mdl_prefix}{self._schema}__{table_name}__v{schema_version}"
            if schema_version != "1_0"
            else f"{self._mdl_prefix}{self._schema}__{table_name}"
        )
        doc_file = (
            f"{self._doc_prefix}{self._schema}__{table_name}__v{schema_version}.yml"
            if schema_version != "1_0"
            else f"{self._doc_prefix}{self._schema}__{table_name}.yml"
        )
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
                    "name": model_name,
                    "description": description,
                    "columns": [],
                }
            ],
        }
        test_cols = list(self._project.artifacts["dbt"]["docs"]["tests"].keys())

        if self._sdk_arg == "segment":
            taken_cols = []  # Used to check for duplicates

            for col in columns:
                if col["name"] == "id":
                    if table_name == "identifies":
                        col_name = "identify_id"
                        taken_cols.append(col_name)
                    elif table_name == "users":
                        col_name = "user_id"
                        taken_cols.append(col_name)
                    elif table_name == "groups":
                        col_name = "group_id"
                        taken_cols.append(col_name)
                    elif table_name == "pages":
                        col_name = "page_id"
                        taken_cols.append(col_name)
                    elif table_name == "screens":
                        col_name = "screen_id"
                        taken_cols.append(col_name)
                    else:  # 'tracks' table and custom events
                        col_name = "event_id"
                        taken_cols.append(col_name)
                elif col["name"] == "event_text":
                    col_name = "event_name"
                    taken_cols.append(col_name)
                else:
                    col_name = (
                        underscore(col["name"])
                        .replace("timestamp", "tstamp")
                        .replace("_at", "_at_tstamp")
                        if "context_" not in underscore(col["name"])
                        else underscore(col["name"]).replace("context_", "")
                    )

                    if col_name in taken_cols:  # Check for duplicates
                        col_name = f"_{col_name}"

                    taken_cols.append(col_name)

                dbt_col = {
                    "name": col_name,
                    "description": col["description"],
                }

                if col["name"] in test_cols:
                    dbt_col["tests"] = self._project.artifacts["dbt"]["docs"]["tests"][
                        col["name"]
                    ]

                doc_obj["models"][0]["columns"].append(dbt_col)

            # Columns describing the call type and where the data came from
            additional_cols = [
                {
                    "name": "call_type",
                    "description": "The type of Segment call (i.e., identify, group, page, screen, track) that collected the data.",  # noqa: E501
                },
                {
                    "name": "source_schema",
                    "description": "The schema where the raw event data is stored.",
                },
                {
                    "name": "source_table",
                    "description": "The table where the raw event data is stored.",
                },
                {
                    "name": "schema_id",
                    "description": "The Reflekt schema ID that governs the event.",
                },
            ]
            doc_obj["models"][0]["columns"].extend(additional_cols)

            if metadata != {}:
                metadata_col = {
                    "name": "schema_metadata",
                    "description": "Schema metadata associated with the event.",
                }
                doc_obj["models"][0]["columns"].append(metadata_col)

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
        print("")

    def build(self) -> None:
        """Build dbt package."""
        print("")
        logger.info(
            f"Building dbt package:"
            f"\n    name: {self._pkg_name}"
            f"\n    dir: {self._pkg_dir}"
            f"\n    --select: {self._select_arg}"
            f"\n    --sdk_arg: {self._sdk_arg}"
            f"\n    --source: {self._source_arg}"
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
        if self._sdk_arg == "segment":
            common_json = (
                self._project.dir
                / "schemas"
                / ".reflekt"
                / "segment"
                / "common"
                / "1-0.json"
            )
        # elif self._sdk_arg == "rudderstack":
        #     pass
        # elif self._sdk_arg == "snowplow":
        #     pass
        # elif self._sdk_arg == "amplitude":
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

        models_config: Dict = self._project.artifacts["dbt"]["models"]
        self._filter = models_config.get("filter", None)

        # Iterate through all schemas to build artifacts
        for schema_path in self._schema_paths:
            logger.info(f"Building dbt artifacts for schema: {schema_path}")

            with schema_path.open("r") as f:
                schema_json = json.load(f)

            schema_id = schema_json["$id"]
            event_name = schema_json["self"]["name"]
            event_desc = schema_json["description"]
            table_name = underscore(event_name.lower().replace(" ", "_"))
            metadata = schema_json["metadata"]

            if self._sdk_arg == "segment":  # Handle Segment-specific table naming
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
            columns_to_search = common_columns + schema_columns
            columns, warehouse_error = self._warehouse.find_columns(
                table_name=table_name,
                columns_to_search=columns_to_search,
            )

            if warehouse_error is not None:
                self.wh_errors.append(warehouse_error)
            else:
                self._build_dbt_table(
                    source=source_obj,
                    table_name=table_name,
                    description=event_desc,
                )
                self._build_dbt_model(
                    schema_id=schema_id,
                    source_schema=self._schema,
                    table_name=table_name,
                    columns=columns,
                    metadata=metadata,
                    filter=self._filter,
                )
                self._build_dbt_doc(
                    schema_id=schema_id,
                    table_name=table_name,
                    description=event_desc,
                    columns=columns,
                    metadata=metadata,
                )

                # Build Segment users table/model/doc
                if self._sdk_arg == "segment" and table_name == "identifies":
                    logger.info(
                        "Building dbt artifacts for schema: [magenta]Segment 'users' table[magenta/]"  # noqa: E501
                    )
                    columns, warehouse_error = self._warehouse.find_columns(
                        table_name="users",
                        columns_to_search=common_columns,
                    )

                    if warehouse_error is not None:
                        self.wh_errors.append(warehouse_error)
                    else:
                        self._build_dbt_table(
                            source=source_obj,
                            table_name="users",
                            description="User traits set by identify() calls.",
                        )
                        self._build_dbt_model(
                            schema_id=schema_id,
                            source_schema=self._schema,
                            table_name="users",
                            columns=columns,
                            metadata={},
                        )
                        self._build_dbt_doc(
                            schema_id=schema_id,
                            table_name="users",
                            description="User traits set by identify() calls.",
                            columns=columns,
                            metadata={},
                        )

        # Build Segment tracks table/model/doc
        if self._sdk_arg == "segment":
            logger.info(
                "Building dbt artifacts for schema: [magenta]Segment 'tracks' table[magenta/]"  # noqa: E501
            )
            columns, warehouse_error = self._warehouse.find_columns(
                table_name="tracks",
                columns_to_search=common_columns,
            )

            if warehouse_error is not None:
                self.wh_errors.append(warehouse_error)
            else:
                self._build_dbt_table(
                    source=source_obj,
                    table_name="tracks",
                    description=(
                        "A summary of track() calls from all events. Properties unique "
                        "to each event's track() call are omitted."
                    ),
                )
                self._build_dbt_model(
                    schema_id=schema_id,
                    source_schema=self._schema,
                    table_name="tracks",
                    columns=columns,
                    metadata={},
                    filter=self._filter,
                )
                self._build_dbt_doc(
                    schema_id="dummy/schema_id/for/tracks/1-0.json",
                    table_name="tracks",
                    description=(
                        "A summary of track() calls from all events. Properties unique "
                        "to each event's track() call are omitted."
                    ),
                    columns=columns,
                    metadata={},
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
                f"The data warehouse returned the following warning(s) while "
                f"building the dbt package."
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
