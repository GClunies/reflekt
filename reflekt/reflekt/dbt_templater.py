# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from loguru import logger
from reflekt.logger import logger_config
from reflekt.reflekt.errors import ReflektProjectError


def template_dbt_config(id, materialized, warehouse_type):
    if materialized == "view":
        config_str = "{{\n" "  config(\n" "    materialized = 'view',\n" "  )\n" "}}\n\n"
    elif materialized == "incremental":
        if warehouse_type == "redshift":
            sort_str = "sort = 'tstamp'"
        elif warehouse_type == "snowflake":
            sort_str = "cluster_by = 'tstamp'"
        config_str = (
            "{{\n"
            f"  config(\n"
            f"    materialized = 'incremental',\n"
            f"    unique_key = '{id}',\n"
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

    return config_str


def template_dbt_source_cte(materialized):
    pass


def template_dbt_renamed_cte():
    pass


def template_dbt_std_columns():
    pass


def template_dbt_unique_columns():
    pass


# flake8: noqa
# fmt: off
dbt_src_schema = {
    "version": 2,
    "sources": [
        {
            "name": "",
            "description": "",
            "tables": []
        }
    ]
}

dbt_table_schema = {
    "name": "",
    "description": "",
    "columns": [],
}

dbt_stg_schema = {
    "version": 2,
    "models": [],
}

dbt_model_schema = {
    "name": "",
    "description": "",
    "columns": [],
}

dbt_column_schema = {
    "name": "",
    "description": "",
}
# fmt: on
