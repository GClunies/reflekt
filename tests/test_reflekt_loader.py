# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import yaml
from reflekt.errors import ReflektValidationError
from reflekt.event import ReflektEvent
from reflekt.loader import ReflektLoader
from reflekt.plan import ReflektPlan

from tests.build import build_reflekt_plan_dir
from tests.fixtures.reflekt_event import REFLEKT_EVENT, REFLEKT_EVENT_BAD
from tests.fixtures.reflekt_plan import REFLEKT_PLAN


def test_loader_reflekt_plan(tmpdir):
    plan_dir = build_reflekt_plan_dir(tmpdir)
    loader = ReflektLoader(plan_dir, "test-plan")
    yaml_obj = yaml.safe_load(REFLEKT_PLAN)
    expected = ReflektPlan(yaml_obj, "test-plan")
    actual = loader.plan

    assert expected.name == actual.name


def test_loader_reflekt_event(tmpdir):
    plan_dir = build_reflekt_plan_dir(tmpdir)
    loader = ReflektLoader(plan_dir, "test-plan")
    yaml_obj = yaml.safe_load(REFLEKT_EVENT)
    expected = ReflektEvent(yaml_obj[0])
    events = loader.plan.events
    actual = events[0]

    assert len(events) == 1
    assert expected.name == actual.name


def test_loader_identify(tmpdir):
    plan_dir = build_reflekt_plan_dir(tmpdir)
    loader = ReflektLoader(plan_dir, "test-plan")
    traits = loader.plan.identify_traits

    assert len(traits) == 4


def test_loader_group(tmpdir):
    plan_dir = build_reflekt_plan_dir(tmpdir)
    loader = ReflektLoader(plan_dir, "test-plan")
    traits = loader.plan.group_traits

    assert len(traits) == 2
