# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import shutil
import subprocess
import typing

from loguru import logger
from reflekt.avo.errors import AvoCliError
from reflekt.logger import logger_config
from reflekt.reflekt.config import ReflektConfig
from reflekt.reflekt.project import ReflektProject


class AvoCli:
    def __init__(self, avo_branch: typing.Optional[str] = None):
        self._project = ReflektProject()
        self._config = ReflektConfig()
        self.type = self._config.plan_type
        self.avo_json_source = self._config.avo_json_source
        self.avo_dir = self._project.project_dir / ".reflekt" / "avo"
        self.avo_branch = avo_branch
        logger.configure(**logger_config)

    def get(self, plan_name):
        plan_db_schemas = self._project.plan_db_schemas
        avo_json_file = self.avo_dir / f"{plan_name}.json"

        if not avo_json_file.exists():
            avo_json_file.touch()
            avo_json_file.write_text("{}")

        if plan_name not in plan_db_schemas:
            raise AvoCliError(
                f"Plan {plan_name} not found in `plan_db_schemas:` in "
                f"{self._project.project_dir}/reflekt_project.yml"
            )
        else:
            self._run_avo_pull(plan_name)
            with open(avo_json_file) as f:
                return json.load(f)

    def _run_avo_pull(self, plan_name):
        logger.info(f"Running `avo pull` to fetch {plan_name} from Avo account.\n")
        avo_executable = shutil.which("avo")
        # Make sure the correct avo branch is checked out
        if self.avo_branch is not None:
            checkout_call = subprocess.call(  # noqa: F841
                args=[
                    avo_executable,
                    "checkout",
                    self.avo_branch,
                ],
                cwd=self.avo_dir,
            )
        else:
            checkout_call = subprocess.call(  # noqa: F841
                args=[
                    avo_executable,
                    "checkout",
                    "main",
                ],
                cwd=self.avo_dir,
            )

        # Run avo pull
        pull_call = subprocess.call(  # noqa: F841
            args=[
                avo_executable,
                "pull",
                plan_name,
                "--force",  # --force flag used in case object type used in plan
            ],
            cwd=self.avo_dir,
        )
        print("")  # Make output look nicer
