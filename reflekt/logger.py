# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import sys

from reflekt.reflekt.project import ReflektProject

if ReflektProject().exists:
    sink = (
        str(ReflektProject().project_dir)
        + "/.reflekt/logs/reflekt_{time:YYYY-MM-DD-HHmmss}.log"
    )
else:
    sink = "./.reflekt/logs/reflekt_{time:YYYY-MM-DD-HHmmss}.log"


logger_config = {
    "handlers": [
        {
            "sink": sys.stdout,
            "format": "{time:HH:mm:ss} {message}",
        },
        {
            "sink": sink,
            "serialize": True,
        },
    ],
}
