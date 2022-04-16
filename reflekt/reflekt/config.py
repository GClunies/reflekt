# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import yaml
from pathlib import Path
from reflekt.reflekt.project import ReflektProject
from reflekt.reflekt.errors import ReflektConfigError
from reflekt.reflekt._global import WAREHOUSES


class ReflektConfig:
    def __init__(self, raise_config_errors=True):
        if ReflektProject().exists:
            try:
                self.config_errors = []
                self.project = ReflektProject()
                self.config_profile = self.project.config_profile

                if self.project.config_path is None:
                    self.path = Path.home() / ".reflekt" / "reflekt_config.yml"
                else:
                    self.path = self.project.config_path

                self.config = self._get_config()
                self.plan_type = self.config.get("plan_type")
                self.avo_json_source = self.config.get("avo_json_source")
                self.cdp_name = self.config.get("cdp")
                self.access_token = self.config.get("access_token")
                self.workspace_name = self.config.get("workspace_name")
                self.warehouse = self.config.get("warehouse")
                self.warehouse_type = self._get_warehouse_type()

            except ReflektConfigError as error:
                if raise_config_errors:
                    raise error
                else:
                    self.config_errors.append(error)

    def _get_config(self):
        try:
            with open(self.path) as f:
                config_yml = yaml.safe_load(f)
            return config_yml[self.config_profile]
        except FileNotFoundError:
            raise ReflektConfigError(
                f"\nNo config file found at: {self.path}\nPlease create one."
            )

    def _get_warehouse_type(self):
        if len(self.warehouse.keys()) > 1:
            raise ReflektConfigError(
                f"More than one warehouse defined in {self.path}\n"
                f"Only one warehouse can be defined."
            )

        warehouse_type = list(self.warehouse.keys())[0]

        if warehouse_type not in WAREHOUSES:
            raise ReflektConfigError(
                f"Unknown warehouse {warehouse_type} specified. Check config "
                f"at {self.path}"
            )

        return warehouse_type
