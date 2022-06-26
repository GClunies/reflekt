# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import sys

from reflekt.project import ReflektProject
from reflekt.utils import log_formatter

if ReflektProject().exists:
    sink = str(ReflektProject().project_dir) + "/.reflekt/logs/reflekt.log"
else:
    sink = "./.reflekt/logs/reflekt.log"

logger_config = {
    "handlers": [
        {
            "sink": sys.stdout,
            "format": log_formatter,
        },
        {
            "sink": sink,
            "format": log_formatter,
        },
    ],
}
