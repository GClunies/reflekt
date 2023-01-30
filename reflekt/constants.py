# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum


SCHEMA_DIALECT = "http://json-schema.org/draft-07/schema#"

REFLEKT_JSON_SCHEMA = {
    "$schema": SCHEMA_DIALECT,
    "$id": "",
    "description": "",
    "self": {
        "vendor": "",
        "name": "",
        "format": "jsonschema",
        "version": "1-0",
    },
    "metadata": {},
    "type": "object",
    "properties": {},
    "required": [],
    "additionalProperties": False,
}

REGISTRY = [
    "avo",
    "segment",
    # "rudderstack",
    # "snowplow Iglu",
    # "amplitude Data",
]


class RegistryEnum(str, Enum):
    """Enum of supported schema registries."""

    avo = "avo"
    segment = "segment"
    # rudderstack = "rudderstack"
    # amplitude = "amplitude"
    # snowplow = "snowplow"


WAREHOUSE = [
    "snowflake",
    "redshift",
    # "bigquery",
]


class WarehouseEnum(str, Enum):
    """Enum of supported data warehouse."""

    snowflake = "snowflake"
    redshift = "redshift"
    # bigquery = "bigquery"


class ArtifactEnum(str, Enum):
    """Enum of supported data artifacts."""

    dbt = "dbt"
    # looker = "looker"
    # lightdash = "lightdash"
    # malloy = "malloy"


class SdkEnum(str, Enum):
    """Enum of supported SDKs that generate event data."""

    segment = "segment"
