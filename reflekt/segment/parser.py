# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
# SPDX-License-Identifier: Apache-2.0
#
# SPDX-FileCopyrightText: 2021 Buffer
# SPDX-License-Identifier: MIT


# The function parse_segment_property is a derivative work based on the
# function parse_property from project tracking-plan-kit licensed under MIT.
# All changes are licensed under Apache-2.0.
def parse_segment_property(name: str, property_json: dict, required: list = []):
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

    if "pattern" in property_json.keys():
        p["pattern"] = property_json.get("pattern")

    if "format" in property_json.keys():
        if property_json.get("format") == "date-time":
            p["datetime"] = True
        else:
            pass

    # If the property data type is 'array' or 'object', use recursion to get
    # any nested item schema or nested property schema. A simple intro to
    # recursion in Python can be found at:
    # https://realpython.com/python-recursion/
    if p["type"] == "array":
        # If a schema for items in the array has been defined in the
        # tracking plan, get the schema.
        if "items" in property_json.keys():
            array_props = []
            reqd_array_props = property_json.get("items").get("required")

            for property_name, property_prop in sorted(
                property_json.get("items").get("properties").items()
            ):
                item_p = parse_segment_property(
                    property_name, property_prop, reqd_array_props
                )  # Using RECURSION
                array_props.append(item_p)
            p["array_item_schema"] = array_props
        return p
    elif p["type"] == "object":
        # If a schema is defined for the object property, get the schema.
        object_props = []
        reqd_object_props = property_json.get("required")

        if "properties" in property_json.keys():
            for property_name, property_prop in sorted(
                property_json.get("properties").items()
            ):
                obj_p = parse_segment_property(
                    property_name, property_prop, reqd_object_props
                )  # Using RECURSION
                object_props.append(obj_p)
            p["object_properties"] = object_props
        return p
    else:
        return p


# The function parse_segment_event is a derivative work based on the
# function parse_event from project tracking-plan-kit licensed under MIT.
# All changes are licensed under Apache-2.0.
def parse_segment_event(event_json: dict):
    metadata_raw = event_json.get("rules").get("labels")

    metadata = {}

    for key, value in sorted(metadata_raw.items()):
        metadata.update({key: value})

    event_obj = {
        "name": event_json.get("name"),
        "description": event_json.get("description"),
        "version": event_json.get("version"),
        "metadata": metadata,
    }
    properties = (
        event_json.get("rules").get("properties").get("properties").get("properties")
    )
    required = (
        event_json.get("rules").get("properties").get("properties").get("required", [])
    )
    event_obj_properties = []

    if properties is None:
        pass
    else:
        for name, prop in sorted(properties.items()):
            # logger.info(f"   Parsing property: {name}")
            p = parse_segment_property(name, prop, required)
            event_obj_properties.append(p)

    event_obj["properties"] = event_obj_properties

    return event_obj
