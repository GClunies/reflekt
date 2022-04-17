# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import sys

logger_config = {
    "handlers": [
        {
            "sink": sys.stdout,
            "format": "{time:HH:mm:ss} {message}",
        },
        {
            "sink": "./.reflekt/logs/reflekt_{time:YYYY-MM-DD-HHmmss}.log",
            "serialize": True,
        },
    ],
}
