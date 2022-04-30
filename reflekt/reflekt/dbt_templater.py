# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0


def template_dbt_config():
    pass


def template_dbt_source_cte():
    pass


def template_dbt_renamed_cte():
    pass


def template_dbt_std_columns():
    pass


def template_dbt_event_columns():
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
