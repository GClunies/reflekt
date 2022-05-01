# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from inflection import titleize, underscore
from loguru import logger

from reflekt.logger import logger_config
from reflekt.reflekt.columns import reflekt_columns
from reflekt.reflekt.errors import ReflektProjectError


def template_dbt_model_config(id, materialized, warehouse_type):
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

    return model_config


def template_dbt_source_cte(source_schema, source_table, incremental_logic=None):
    if incremental_logic is None:
        incremental_logic = ""
    source_cte = (
        "with\n\n"
        "source as (\n\n"
        f"    select *\n\n"
        f"    from source {{{{ source('{underscore(source_schema)}', '{source_table}') }}}}\n\n"
        f"    {incremental_logic}\n\n"
        ")\n\n"
    )

    return source_cte


def template_dbt_source():
    pass


def template_dbt_renamed_cte(cdp_columns_dict, db_columns):
    # fmt: off
    renamed_cte = (
        "renamed as (\n\n"
        "    select"
    )
    # fmt: on


def template_dbt_std_columns(renamed_cte, std_columns):
    pass


def template_dbt_unique_columns(renamed_cte, unique_columns):
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
