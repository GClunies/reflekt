# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import os

from dotenv import load_dotenv


__version__ = "0.3.1"


load_dotenv()  # load environment variables from .env file (if exists)

SHOW_LOCALS = os.getenv("REFLEKT_SHOW_LOCALS") == "true"
