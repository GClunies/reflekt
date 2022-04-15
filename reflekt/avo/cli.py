# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import subprocess
import shutil
import json
from loguru import logger
from reflekt.logger import logger_config
from reflekt.reflekt.project import ReflektProject
from reflekt.reflekt.config import ReflektConfig
from reflekt.avo.errors import AvoCliError


class AvoCli:
    def __init__(self):
        self.project = ReflektProject()
        self.project_dir = self.project.project_dir
        self.config = ReflektConfig()
        self.config_path = self.config.path
        self.avo_json_source = self.config.avo_json_source
        self.avo_dir = self.project_dir / ".reflekt" / "avo"
        logger.configure(**logger_config)

    def get(self, plan_name):
        if plan_name != self.avo_json_source:
            raise AvoCliError(
                f"Plan name {plan_name} does not match 'avo_json_source: {self.avo_json_source}' "
                f"specified in {self.config_path}"
            )

        else:
            self._run_avo_pull()
            avo_json_file = self.avo_dir / f"{self.avo_json_source}.json"
            with open(avo_json_file) as f:
                avo_json = json.load(f)

            return avo_json

    def _run_avo_pull(self):
        logger.info(f"Running `avo pull` to fetch {self.avo_json_source} from Avo account.\n")
        avo_executable = shutil.which("avo")
        subprocess.call([avo_executable, "pull", self.avo_json_source], cwd=self.avo_dir)
