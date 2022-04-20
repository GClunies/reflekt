# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import yaml

from reflekt.reflekt.errors import ReflektValidationError
from reflekt.reflekt.event import ReflektEvent
from reflekt.reflekt.loader import ReflektLoader
from reflekt.reflekt.plan import ReflektPlan
from tests.fixtures import (
    REFLEKT_EVENT,
    REFLEKT_EVENT_BAD,
    REFLEKT_GROUP,
    REFLEKT_IDENTIFY,
    REFLEKT_PLAN,
)


def _create_reflekt_plan(tmp_dir, event_contents=REFLEKT_EVENT):
    plan_dir = tmp_dir.mkdir("tracking-plans").mkdir("test-plan")
    _create_reflekt_plan_yml(plan_dir)
    _create_reflekt_identify(plan_dir)
    _create_reflekt_group(plan_dir)
    _create_reflekt_event(plan_dir, event_contents)

    return plan_dir


def _create_reflekt_plan_yml(tmp_dir):
    r_prop = tmp_dir / "plan.yml"
    r_prop.write(REFLEKT_PLAN)


def _create_reflekt_event(tmp_dir, event_contents):
    r_event = tmp_dir.mkdir("events") / "test-event.yml"
    r_event.write(event_contents)


def _create_reflekt_identify(tmp_dir):
    r_identify = tmp_dir / "identify_traits.yml"
    r_identify.write(REFLEKT_IDENTIFY)


def _create_reflekt_group(tmp_dir):
    r_group = tmp_dir / "group_traits.yml"
    r_group.write(REFLEKT_GROUP)


def test_loader_reflekt_plan(tmpdir):
    plan_dir = _create_reflekt_plan(tmpdir)
    loader = ReflektLoader(plan_dir, "test-plan")
    yaml_obj = yaml.safe_load(REFLEKT_PLAN)
    expected = ReflektPlan(yaml_obj, "test-plan")
    actual = loader.plan

    assert expected.name == actual.name


def test_loader_reflekt_event(tmpdir):
    plan_dir = _create_reflekt_plan(tmpdir)
    loader = ReflektLoader(plan_dir, "test-plan")
    yaml_obj = yaml.safe_load(REFLEKT_EVENT)
    expected = ReflektEvent(yaml_obj[0])
    events = loader.plan.events
    actual = events[0]

    assert len(events) == 1
    assert expected.name == actual.name


def test_loader_identify(tmpdir):
    plan_dir = _create_reflekt_plan(tmpdir)
    loader = ReflektLoader(plan_dir, "test-plan")
    traits = loader.plan.identify_traits

    assert len(traits) == 4


def test_loader_group(tmpdir):
    plan_dir = _create_reflekt_plan(tmpdir)
    loader = ReflektLoader(plan_dir, "test-plan")
    traits = loader.plan.group_traits

    assert len(traits) == 2


def test_loader_validation(tmpdir):
    # Create tracking plan with bad event (missing required name)
    plan_dir = _create_reflekt_plan(tmpdir, event_contents=REFLEKT_EVENT_BAD)

    with pytest.raises(ReflektValidationError):
        ReflektLoader(plan_dir, "test-plan")


def test_loader_collect_validation_errors(tmpdir):
    # Create tracking plan with bad event (missing required name)
    plan_dir = _create_reflekt_plan(tmpdir, event_contents=REFLEKT_EVENT_BAD)
    loader = ReflektLoader(plan_dir, "test-plan", raise_validation_errors=False)

    assert loader.has_validation_errors
    assert len(loader.validation_errors) == 1
