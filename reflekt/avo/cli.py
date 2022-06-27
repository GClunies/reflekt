# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import shutil
import subprocess
from typing import Optional

from loguru import logger

from reflekt.config import ReflektConfig
from reflekt.logger import logger_config
from reflekt.project import ReflektProject


class AvoCli:
    def __init__(self, avo_branch: Optional[str] = None) -> None:
        self._project = ReflektProject()
        self._config = ReflektConfig()
        self.type = self._config.plan_type
        self.avo_dir = self._project.project_dir / ".reflekt" / "avo"
        self.avo_branch = avo_branch
        logger.configure(**logger_config)

    def get(self, plan_name: str) -> None:
        # warehouse_schemas = self._project.warehouse_schemas
        avo_json_file = self.avo_dir / f"{plan_name}.json"

        if not avo_json_file.exists():
            avo_json_file.touch()
            avo_json_file.write_text("{}")

        self._run_avo_pull(plan_name)

        with open(avo_json_file) as f:
            return json.load(f)

    def _run_avo_pull(self, plan_name: str) -> None:
        logger.info(f"Fetching plan {plan_name} from Avo.\n")
        avo_executable = shutil.which("avo")

        # Use the provided --avo-branch argument if one was provided
        if self.avo_branch is not None:
            subprocess.call(
                args=[
                    avo_executable,
                    "pull",
                    plan_name,
                    "--force",  # --force flag used in case object type used in plan
                    "--branch",
                    self.avo_branch,
                ],
                cwd=self.avo_dir,
            )
        else:
            subprocess.call(
                args=[
                    avo_executable,
                    "pull",
                    plan_name,
                    "--force",  # --force flag used in case object type used in plan
                ],
                cwd=self.avo_dir,
            )

        logger.info("")  # Terminal newline
