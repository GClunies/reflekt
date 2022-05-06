# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import yaml

from reflekt.reflekt.errors import ReflektValidationError
from reflekt.reflekt.plan import ReflektPlan
from tests.fixtures import (
    REFLEKT_EVENT,
    REFLEKT_GROUP,
    REFLEKT_IDENTIFY,
    REFLEKT_PLAN,
    REFLEKT_PLAN_BAD,
)


def test_reflekt_plan():
    plan = ReflektPlan(yaml.safe_load(REFLEKT_PLAN), "test-plan")

    assert plan.name == "test-plan"


def test_add_event():
    plan = ReflektPlan(yaml.safe_load(REFLEKT_PLAN), "test-plan")
    plan.add_event(yaml.safe_load(REFLEKT_EVENT)[0])

    assert len(plan.events) == 1


def test_add_identify_trait():
    plan = ReflektPlan(yaml.safe_load(REFLEKT_PLAN), "test-plan")
    yaml_obj = yaml.safe_load(REFLEKT_IDENTIFY)
    trait = yaml_obj["traits"][0]
    plan.add_identify_trait(trait)

    assert len(plan.identify_traits) == 1


def test_add_group_trait():
    plan = ReflektPlan(yaml.safe_load(REFLEKT_PLAN), "test-plan")
    yaml_obj = yaml.safe_load(REFLEKT_GROUP)
    trait = yaml_obj["traits"][0]
    plan.add_group_trait(trait)

    assert len(plan.group_traits) == 1


def test_duplicate_events():
    plan = ReflektPlan(yaml.safe_load(REFLEKT_PLAN), "test-plan")
    # Add the same event twice
    plan.add_event(yaml.safe_load(REFLEKT_EVENT)[0])
    plan.add_event(yaml.safe_load(REFLEKT_EVENT)[0])

    with pytest.raises(ReflektValidationError):
        plan.validate_plan()


def test_plan_validation():
    plan_good = ReflektPlan(yaml.safe_load(REFLEKT_PLAN), "test-plan")
    plan_bad = ReflektPlan(
        yaml.safe_load(REFLEKT_PLAN_BAD), "test-plan"
    )  # Missing `name:``

    assert plan_good.validate_plan() is None

    with pytest.raises(ReflektValidationError):
        plan_bad.validate_plan()