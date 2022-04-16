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
        self._project = ReflektProject()
        self._config = ReflektConfig()
        self.type = self._config.plan_type
        self.avo_json_source = self._config.avo_json_source
        self.avo_dir = self._project.project_dir / ".reflekt" / "avo"
        logger.configure(**logger_config)

    def get(self, plan_name):
        if plan_name != self.avo_json_source:
            raise AvoCliError(
                f"Plan name {plan_name} does not match 'avo_json_source: "
                f"{self.avo_json_source}' specified in {self._config.config_path}"
            )
        else:
            self._run_avo_pull()
            avo_json_file = self.avo_dir / f"{self.avo_json_source}.json"
            with open(avo_json_file) as f:
                return json.load(f)

    def _run_avo_pull(self):
        logger.info(
            f"Running `avo pull` to fetch {self.avo_json_source} from Avo account.\n"
        )
        avo_executable = shutil.which("avo")
        subprocess.call(
            [avo_executable, "pull", self.avo_json_source],
            cwd=self.avo_dir,
        )
        print("")  # Make output look nicer
