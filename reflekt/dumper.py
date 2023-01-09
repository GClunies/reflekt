# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import yaml


class ReflektYamlDumper(yaml.Dumper):
    """Custom YAML dumper class. Indents list object for readability."""

    def increase_indent(self, flow: bool = False, indentless: bool = False):
        """Increase indentation level."""  # noqa: DAR101, DAR201
        return super(ReflektYamlDumper, self).increase_indent(flow, False)

    def ignore_aliases(self, data):
        """Don't use YAML anchors/aliases.

        https://ttl255.com/yaml-anchors-and-aliases-and-how-to-disable-them/
        """  # noqa: DAR101, DAR201
        return True
