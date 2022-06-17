# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0


def parse_avo_property(name: str, property_json: dict, required: list = []) -> dict:
    p_types = property_json.get("type")
    if not isinstance(p_types, (list,)):
        p_types = [p_types]  # If p_types is not list, make it one

    if not p_types[0]:
        p_types[0] = "any"

    p = {
        "name": name,
        "description": property_json.get("description"),
        "type": p_types[0],
    }
    allow_null = len(p_types) > 1 and p_types[1] == "null"

    if allow_null:
        p["allow_null"] = True

    if required is not None and name in required:
        p["required"] = True

    if "enum" in property_json.keys():
        p["enum"] = property_json.get("enum")

    if p["type"] == "array":
        # Unlike Segment, Avo takes a simplified approach to array types, user
        # can only specify the type of the array elements. No 'array items'
        # like Segment. This placeholder is kept in case this changes.
        return p

    elif p["type"] == "object":
        object_props = []
        reqd_object_props = property_json.get("required")

        if "properties" in property_json.keys():
            for property_name, property_prop in property_json.get("properties").items():
                obj_p = parse_avo_property(
                    property_name, property_prop, reqd_object_props
                )  # Using RECURSION
                object_props.append(obj_p)
            p["object_properties"] = object_props

        return p

    else:
        return p


def parse_avo_event(event_json: dict) -> dict:
    tags = event_json.get("tags")
    metadata_raw = {
        tag.split(":")[0]: tag.split(":")[1].replace(" ", "") for tag in tags
    }
    metadata = {}

    for key, value in sorted(metadata_raw.items()):
        metadata.update({key: value})

    event_obj = {
        "name": event_json.get("name"),
        "description": event_json.get("description"),
        "metadata": metadata,
    }
    properties_lvl2 = event_json.get("rules").get("properties").get("properties")

    if properties_lvl2 is not None:
        properties = properties_lvl2.get("properties")
        required = properties_lvl2.get("required", [])
    else:
        properties = None
        required = []

    event_obj_properties = []

    if properties is None:
        pass
    else:
        for name, prop in sorted(properties.items()):
            # logger.info(f"Dumping property: {name}")
            p = parse_avo_property(name, prop, required)
            event_obj_properties.append(p)

    event_obj["properties"] = event_obj_properties

    return event_obj
