# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

# fmt: off
WAREHOUSES = [
    "snowflake",
    "redshift",
]

WAREHOUSE_INIT_STRING = (
    "\n[1] Snowflake"
    "\n[2] Redshift"
)

WAREHOUSE_MAP = {
    "1": "snowflake",
    "2": "redshift",
}
