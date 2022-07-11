# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

# fmt: off
segment_payload_schema = {
    "update_mask": {
        "paths": [
            "tracking_plan.display_name",
            "tracking_plan.rules"
        ]
    },
    "tracking_plan": {}
}

segment_plan_schema = {
    "display_name": "",
    "rules": {
        "user_traits": [],
        "group_traits": [],
        "events": [],
        "global": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "properties": {},
                "context": {},
                "traits": {}
            }
        },
        "identify": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "properties": {},
                "context": {},
                "traits": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        "group": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "properties": {},
                "context": {},
                "traits": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    }
}

segment_event_schema = {
    "name": "",
    "description": "",
    "version": 1,
    "rules": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "labels": {},
        "properties": {
            "context": {},
            "traits": {},
            "properties": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
}

segment_property_schema = {
    "description": "",
    "type": "",
}

segment_items_schema = {
    "items": {
        "type": "object",
        "properties": {},
        "required": [],
    }
}
