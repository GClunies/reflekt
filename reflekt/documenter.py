# SPDX-FileCopyrightText: 2023 Amaury Faure <amaury2650@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import json

from reflekt.project import Project


class Documenter:
    """Reflekt Documenter class.

    Creates documentation as md for schemas declarer in reflekt.
    """

    def __init__(self, project: Project) -> None:
        """Initialize Reflekt Documenter.

        Args:
            project (Project): Reflekt project object.
        """
        self._project = project
        self._meta_path = self._project.dir / "schemas/.reflekt/meta/1-0.json"

        with self._meta_path.open() as f:
            self._meta_schema = json.load(f)

    def key_value_pair_to_str(self, key, value):
        if type(value) == type([]):
            value = "\n\n   - " + "\n\n - ".join(value)
        return f"**{key}** : {value} \n\n"

    def property_to_md(self, property_name, property_detail, is_required=False):
        requirement = "Optional"
        if is_required:
            requirement = "Required"

        output = f"### {property_name} ({requirement}) \n\n"
        for key in property_detail:
            output += "- " + self.key_value_pair_to_str(
                key, property_detail["description"]
            )
        return output

    def reflekt_to_md(self, jsonschema_file, output_file):
        with open(jsonschema_file, "r") as f:
            schema = json.load(f)

        introduction_properties = ["description", "$id"]

        # Introduction
        md_output = f"# {schema['self']['name']}  \n\n"
        for key in schema:
            if key in introduction_properties:
                md_output += "- " + self.key_value_pair_to_str(key, schema[key])
        # Metadata
        for key in schema["self"]["metadata"]:
            md_output += "- " + self.key_value_pair_to_str(
                key, schema["self"]["metadata"][key]
            )
        # Properties
        md_output += f"## Properties \n\n"
        for property_name in schema["properties"]:
            is_required = property_name in schema["required"]
            md_output += self.property_to_md(
                property_name, schema["properties"][f"{property_name}"], is_required
            )

        # Required Properties
        md_output += f"## Required\n\n"
        md_output += "\n\n   - " + "\n\n - ".join(schema["required"])

        # Write the Markdown content to the output file
        with open(output_file, "w") as f:
            f.write(md_output)
