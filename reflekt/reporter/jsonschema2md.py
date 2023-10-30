# SPDX-FileCopyrightText: 2023 Stéphane Brunner
#
# SPDX-License-Identifier: Apache-2.0

# This file contains derivative works based on:
# https://github.com/sbrunner/jsonschema2md/blob/908ecb1e40c8b717659e553ee12925d11608a7bd/jsonschema2md/__init__.py
#
# Changes are made to modify the `Parser` class to fit the needs of Reflekt.

from __future__ import annotations

import io
import json
import re
from typing import Optional, Union


class JSONParser:
    """JSON Schema to Markdown parser."""

    tab_size = 2

    def __init__(self, show_examples: str = "all"):
        """Initialize JSONParser class.

        Args:
            show_examples (str): Parse examples for only the main object, only for
                properties, or for all. Defaults to "all".

        Raises:
            ValueError: If `show_examples` is not one of "all", "object", or
                "properties".
        """
        valid_show_examples_options = ["all", "object", "properties"]
        show_examples = show_examples.lower()

        if show_examples in valid_show_examples_options:
            self.show_examples = show_examples
        else:
            raise ValueError(
                f"`show_examples` option should be one of "
                f"`{valid_show_examples_options}`; `{show_examples}` was passed."
            )

    def _construct_description_line(
        self, obj: dict, add_type: bool = False
    ) -> list[str]:
        """Construct description line of property, definition, or item.

        Args:
            obj (dict): JSON Schema object.
            add_type (bool): Whether to add the type to the description line.
                Defaults to False.

        Returns:
            list[str]: Description line as a list of strings.
        """
        description_line = []

        if "description" in obj:
            ending = "" if re.search(r"[.?!;]$", obj["description"]) else "."
            description_line.append(f"{obj['description']}{ending}")

        if add_type:
            if "type" in obj:
                description_line.append(f"Must be of type *{obj['type']}*.")

        if "minimum" in obj:
            description_line.append(f"Minimum: `{obj['minimum']}`.")

        if "exclusiveMinimum" in obj:
            description_line.append(f"Exclusive minimum: `{obj['exclusiveMinimum']}`.")

        if "maximum" in obj:
            description_line.append(f"Maximum: `{obj['maximum']}`.")

        if "exclusiveMaximum" in obj:
            description_line.append(f"Exclusive maximum: `{obj['exclusiveMaximum']}`.")

        if "minItems" in obj or "maxItems" in obj:
            length_description = "Length must be "

            if "minItems" in obj and "maxItems" not in obj:
                length_description += f"at least {obj['minItems']}."
            elif "maxItems" in obj and "minItems" not in obj:
                length_description += f"at most {obj['maxItems']}."
            elif obj["minItems"] == obj["maxItems"]:
                length_description += f"equal to {obj['minItems']}."
            else:
                length_description += (
                    f"between {obj['minItems']} and {obj['maxItems']} (inclusive)."
                )

            description_line.append(length_description)

        if "enum" in obj:
            description_line.append(f"Must be one of: `{json.dumps(obj['enum'])}`.")

        if "additionalProperties" in obj:
            if obj["additionalProperties"]:
                description_line.append("Can contain additional properties.")
            else:
                description_line.append("Cannot contain additional properties.")

        if "$ref" in obj:
            description_line.append(f"Refer to *[{obj['$ref']}](#{obj['$ref'][2:]})*.")

        if "default" in obj:
            description_line.append(f"Default: `{json.dumps(obj['default'])}`.")

        # Only add start colon if items were added
        if description_line:
            description_line.insert(0, ":")

        return description_line

    def _construct_examples(
        self, obj: dict, indent_level: int = 0, add_header: bool = True
    ) -> list[str]:
        def dump_json_with_line_head(obj, line_head, **kwargs):
            result = [
                line_head + line
                for line in io.StringIO(json.dumps(obj, **kwargs)).readlines()
            ]

            return "".join(result)

        example_lines = []
        if "examples" in obj:
            example_indentation = " " * self.tab_size * (indent_level + 1)

            if add_header:
                example_lines.append(f"\n{example_indentation}Examples:\n")

            for example in obj["examples"]:
                lang = "json"
                dump_fn = dump_json_with_line_head
                example_str = dump_fn(example, line_head=example_indentation, indent=4)
                example_lines.append(
                    f"{example_indentation}"
                    f"```{lang}\n{example_str}\n{example_indentation}```\n\n"
                )

        return example_lines

    def _parse_object(
        self,
        obj: Union[dict, list],
        name: Optional[str],
        name_monospace: bool = True,
        output_lines: Optional[list[str]] = None,
        indent_level: int = 0,
        path: Optional[list[str]] = None,
        required: bool = True,
    ) -> list[str]:
        """Parse JSON object and its items, definitions, and properties recursively.

        Args:
            obj (Union[dict, list]): JSON Schema object.
            name (Optional[str]): Name of the object.
            name_monospace (bool): Whether to format the name in monospace.
                Defaults to True.
            output_lines (Optional[list[str]]): Output lines to append to.
                Defaults to None.
            indent_level (int): Indentation level. Defaults to 0.
            path (Optional[list[str]]): Path to the object. Defaults to None.
            required (bool): Whether to include "required" in the description line.

        Returns:
            list[str]: Output lines.

        Raises:
            TypeError: If a non-object type is found in the properties list.
        """

        if not output_lines:
            output_lines = []

        indentation = " " * self.tab_size * indent_level
        indentation_items = " " * self.tab_size * (indent_level + 1)

        if isinstance(obj, list):
            output_lines.append(f"{indentation}- **{name}**:\n")

            for element in obj:
                output_lines = self._parse_object(
                    element,
                    None,
                    name_monospace=False,
                    output_lines=output_lines,
                    indent_level=indent_level + 2,
                )
            return output_lines

        if not isinstance(obj, dict):
            raise TypeError(
                f"Non-object type found in properties list: `{name}: {obj}`."
            )

        # Construct full description line
        description_line_base = self._construct_description_line(obj)
        description_line = list(
            map(
                lambda line: line.replace("\n\n", "<br>" + indentation_items),
                description_line_base,
            )
        )

        # Add full line to output
        description_line = " ".join(description_line)
        optional_format = f", format: {obj['format']}" if "format" in obj else ""

        if name is None:
            obj_type = f"*{obj['type']}{optional_format}*" if "type" in obj else ""
            name_formatted = ""
        else:
            required_str = ", required" if required else ""
            obj_type = (
                f" *({obj['type']}{optional_format}{required_str})*"
                if "type" in obj
                else ""
            )
            name_formatted = f"**`{name}`**" if name_monospace else f"**{name}**"

        anchor = f"<a id=\"{'/'.join(path)}\"></a>" if path else ""
        output_lines.append(
            f"{indentation}- {anchor}{name_formatted}{obj_type}{description_line}\n"
        )

        # Recursively parse subschemas following schema composition keywords
        schema_composition_keyword_map = {
            "allOf": "All of",
            "anyOf": "Any of",
            "oneOf": "One of",
        }

        for key, label in schema_composition_keyword_map.items():
            if key in obj:
                output_lines.append(f"{indentation_items}- **{label}**\n")

                for child_obj in obj[key]:
                    output_lines = self._parse_object(
                        child_obj,
                        None,
                        name_monospace=False,
                        output_lines=output_lines,
                        indent_level=indent_level + 2,
                    )

        # Recursively add items and definitions
        for property_name in ["items", "definitions"]:
            if property_name in obj:
                output_lines = self._parse_object(
                    obj[property_name],
                    property_name.capitalize(),
                    name_monospace=False,
                    output_lines=output_lines,
                    indent_level=indent_level + 1,
                )

        # Recursively add additional child properties
        if "additionalProperties" in obj and isinstance(
            obj["additionalProperties"], dict
        ):
            output_lines = self._parse_object(
                obj["additionalProperties"],
                "Additional Properties",
                name_monospace=False,
                output_lines=output_lines,
                indent_level=indent_level + 1,
            )

        # Recursively add child properties
        for property_name in ["properties", "patternProperties"]:
            if property_name in obj:
                for property_name, property_obj in obj[property_name].items():
                    output_lines = self._parse_object(
                        property_obj,
                        property_name,
                        output_lines=output_lines,
                        indent_level=indent_level + 1,
                        required=property_name in obj.get("required", []),
                    )

        # Add examples
        if self.show_examples in ["all", "properties"]:
            output_lines.extend(
                self._construct_examples(obj, indent_level=indent_level)
            )

        return output_lines

    def parse_schema(self, schema_object: dict) -> list[str]:
        """Parse JSON Schema object to Markdown text.

        Args:
            schema_object (dict): JSON Schema object.

        Returns:
            list[str]: Markdown text.
        """
        output_lines = []

        # Add title and description
        if "self" in schema_object and "name" in schema_object["self"]:
            output_lines.append(f"# {schema_object['self']['name']}\n\n")

        # Add schema ID for reference
        if "$id" in schema_object:
            output_lines.append(f"#### `$id: {schema_object['$id']}`\n\n")

        # Add description
        if "description" in schema_object:
            output_lines.append(f"*{schema_object['description']}*\n\n")

        # Add items
        if "items" in schema_object:
            output_lines.append("## Items\n\n")
            output_lines.extend(
                self._parse_object(
                    schema_object["items"], "Items", name_monospace=False
                )
            )

        # Add additional properties
        if "additionalProperties" in schema_object and isinstance(
            schema_object["additionalProperties"], dict
        ):
            output_lines.append("## Additional Properties\n\n")
            output_lines.extend(
                self._parse_object(
                    schema_object["additionalProperties"],
                    "Additional Properties",
                    name_monospace=False,
                )
            )

        # Add pattern properties
        if "patternProperties" in schema_object:
            output_lines.append("## Pattern Properties\n\n")

            for obj_name, obj in schema_object["patternProperties"].items():
                output_lines.extend(self._parse_object(obj, obj_name))

        # Add properties and definitions
        for name in ["properties", "definitions"]:
            if name in schema_object:
                output_lines.append(f"## {name.capitalize()}\n\n")

                for obj_name, obj in schema_object[name].items():
                    path = [name, obj_name] if name == "definitions" else []
                    output_lines.extend(self._parse_object(obj, obj_name, path=path))

        # Add examples
        if "examples" in schema_object and self.show_examples in ["all", "object"]:
            output_lines.append("## Examples\n\n")
            output_lines.extend(
                self._construct_examples(
                    schema_object, indent_level=0, add_header=False
                )
            )

        return output_lines
