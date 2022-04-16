# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

# fmt: off
PLANS = [
    "avo",
    "segment",
    # "rudderstack",
    # "snowplow",
    # "iteratively",
]

CDPS = [
    "segment",
    # "rudderstack",
    # "snowplow",
]

CDP_INIT_STRING = (
    "\n[1] Segment"
    # "\n[2] Rudderstack"
    # "\n[3] Snowplow"
)

CDP_MAP = {
    "1": "segment",
    # "2": "rudderstack",
    # "3": "snowplow",
}

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
# fmt: on
