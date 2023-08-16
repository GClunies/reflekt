# SPDX-FileCopyrightText: 2023 Amaury Faure <amaury2650@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import json


class Documenter:
    """Reflekt Documenter class.

    Creates documentation as md for schemas declarer in reflekt.
    """

    def __init__(self) -> None:
        """Initialize Reflekt Documenter."""

    def key_value_pair_to_str(self, key, value):
        """
        Convert a key-value pair into a formatted string.

        Args:
            key (str): The key of the pair.
            value (str or list): The corresponding value of the pair.

        Returns:
            str: A formatted string representation of the key-value pair.
        """
        if key.startswith("$"):
            key = key[1:]
        if key == "enum":
            key = "Allowed Values"
        if isinstance(value, list):
            value = "\n\n   - " + "\n\n   - ".join(value)
        return f"**{key}** : {value} \n\n"

    def property_to_md(self, property_name, property_detail, is_required=False):
        """
        Convert property details into a Markdown formatted string.

        Args:
            property_name (str): The name of the property.
            property_detail (dict): A dictionary containing property details as key-value pairs.
            is_required (bool, optional): Specifies whether the property is required or optional. Default is False.

        Returns:
            str: A Markdown formatted string representing the property details.
        """
        # Determine the requirement based on the 'is_required' parameter
        requirement = "Optional"
        if is_required:
            requirement = "Required"

        # Create the heading for the property with its name and requirement status
        output = f"### {property_name} ({requirement}) \n\n"

        # Convert each key-value pair in property_detail to a formatted string
        for key in property_detail:
            output += "- " + self.key_value_pair_to_str(key, property_detail[key])

        return output

    def reflekt_to_md(self, jsonschema_file, output_file):
        """
        Convert a Reflekt JSON schema to Markdown documentation.

        Args:
            jsonschema_file (str): The path to the JSON schema file.
            output_file (str): The path to the output Markdown file.

        Returns:
            None
        """
        with open(jsonschema_file, "r") as f:
            schema = json.load(f)

        introduction_properties = ["description", "$id"]

        # Create the main Markdown content
        md_output = f"# {schema['self']['name']}  \n\n"

        # Extract and include introduction properties
        for key in schema:
            if key in introduction_properties:
                md_output += "- " + self.key_value_pair_to_str(key, schema[key])

        # Include metadata properties
        for key in schema["self"]["metadata"]:
            md_output += "- " + self.key_value_pair_to_str(
                key, schema["self"]["metadata"][key]
            )

        # Include the original json
        md_output += (
            f"<details><summary>JSON format</summary>\n\n```json\n"
            f"{json.dumps(schema, indent=4)} \n "
            f"```\n </details> \n\n"
        )

        # Include properties details
        md_output += f"## Properties \n\n"
        for property_name in schema["properties"]:
            is_required = property_name in schema["required"]
            md_output += self.property_to_md(
                property_name, schema["properties"][property_name], is_required
            )

        # Include required properties
        md_output += f"## Required\n\n"
        md_output += "\n\n   - " + "\n\n - ".join(schema["required"])

        # Write the Markdown content to the output file
        with open(output_file, "w") as f:
            f.write(md_output)
