# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

TITLE_CASE_RE = r"[A-Z][a-z]+"
CAMEL_CASE_RE = r"(^[a-z]|[A-Z])[a-z]*"
SNAKE_CASE_RE = r"^[a-z._]+$"

REFLEKT_INJECTED_COLUMNS = [  # Columns Reflekt injects when templating
    "source_schema",
    "source_table",
    "tracking_plan",
    "event_text",
    "call_type",
]

# Columns reserved by Reflekt templater. If found in table, prefix with underscore (_)
REFLEKT_TEMPLATED_COLUMNS = [
    "id",
    "user_id",
    "anonymous_id",
    "user_id",
    "group_id",
    "page_id",
    "screen_id",
    "event_id",
    "source_schema",
    "source_table",
    "tracking_plan",
    "event_name",
    "call_type",
]

PLANS = [
    "segment",
    "avo",
    # "rudderstack",
    # "snowplow",
]

PLAN_INIT_STRING = (
    "\n[1] Segment Protocols"
    "\n[2] Avo"
    # "\n[3] Rudderstack"
    # "\n[4] Snowplow"
)

PLAN_MAP = {
    "1": "segment",
    "2": "avo",
    # "3": "rudderstack",
    # "4": "snowplow",
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

WAREHOUSE_INIT_STRING = "\n[1] Snowflake" "\n[2] Redshift"

WAREHOUSE_MAP = {
    "1": "snowflake",
    "2": "redshift",
}
