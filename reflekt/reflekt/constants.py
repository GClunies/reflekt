# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

# fmt: off
PLANS = [
    "segment",
    "avo",
    # "rudderstack",
    # "snowplow",
    # "iteratively",
]

PLAN_INIT_STRING = (
    "\n[1] Segment Protocols"
    "\n[2] Avo"
    # "\n[3] Rudderstack"
    # "\n[4] Snowplow"
    # "\n[5] Iteratively"
)

PLAN_MAP = {
    "1": "segment",
    "2": "avo",
    # "3": "rudderstack",
    # "4": "snowplow",
    # "5": "iteratively",
}

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
