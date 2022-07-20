# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import yaml
from loguru import logger

from reflekt.constants import WAREHOUSES
from reflekt.project import ReflektProject


class ReflektConfig:
    def __init__(self) -> None:
        if ReflektProject().exists:
            self.config_errors: list = []
            self.project = ReflektProject()
            self.config_profile: str = self.project.config_profile

            if self.project.config_path is None:
                self.path = Path.home() / ".reflekt" / "reflekt_config.yml"
            else:
                self.path = self.project.config_path

            self.config: dict = self._get_config()
            self.plan_type: str = self.config.get("plan_type")
            self.cdp_name: str = self.config.get("cdp")
            self.access_token: str = self.config.get("access_token")
            self.workspace_name: str = self.config.get("workspace_name")
            self.warehouse: str = self.config.get("warehouse")
            self.warehouse_type: str = self._get_warehouse_type()

    def _get_config(self) -> dict:
        try:
            with open(self.path) as f:
                config_yml: dict = yaml.safe_load(f)
            return config_yml[self.config_profile]
        except FileNotFoundError:
            logger.error(
                f"\nNo reflekt_config.yml file found at: {self.path}. Please create one."
                f" See the Reflekt docs (https://bit.ly/reflekt-profile-config) on "
                f"profile configuration."
            )
            raise SystemExit(1)

    def _get_warehouse_type(self) -> str:
        if len(self.warehouse.keys()) > 1:
            logger.error(
                f"Multiple warehouses defined for 'config_profile: "
                f" {self.config_profile}' in reflekt_config.yml at {self.path}. Only "
                f"one warehouse can be defined per profile. See the Reflekt docs "
                f"(https://bit.ly/reflekt-profile-config) on profile configuration."
            )
            raise SystemExit(1)

        warehouse_type: str = list(self.warehouse.keys())[0]

        if warehouse_type not in WAREHOUSES:
            logger.error(
                f"Unknown warehouse '{warehouse_type}' specified in reflekt_config.yml "
                f"at {self.path}. Valid warehouses: {WAREHOUSES}"
            )
            raise SystemExit(1)

        return warehouse_type
