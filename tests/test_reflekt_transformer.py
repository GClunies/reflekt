# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0


import pytest
import yaml

from reflekt.reflekt.errors import ReflektValidationError
from reflekt.reflekt.event import ReflektEvent
from reflekt.reflekt.loader import ReflektLoader
from reflekt.reflekt.plan import ReflektPlan
from reflekt.reflekt.transformer import ReflektTransformer
from tests.fixtures import (
    REFLEKT_EVENT,
    REFLEKT_EVENT_BAD,
    REFLEKT_GROUP,
    REFLEKT_IDENTIFY,
    REFLEKT_PLAN,
)


# TODO - tests
#    - Transform plan from reflekt spec to Segment json
#    - Transform plan from reflekt spec to Iglu schema json (wait for Iglu integration)
#    - Transform plan from reflekt spec to dbt package
def test_reflekt_transformer():
    pass
